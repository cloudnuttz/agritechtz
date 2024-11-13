"""Harvest Module"""

import os
import tempfile
import re
import urllib.parse

from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Set, Tuple

from bs4 import BeautifulSoup
import httpx
import numpy as np
import pandas as pd
from PyPDF2 import PdfReader

from agritechtz.constants import (
    CROPS_COLUMNS,
    DATE_PATTERN,
    DATE_PATTERN_WITH_MONTH_FIRST,
    PAGES_PATTERN,
    PDF_PATTERN,
    REGIONAL_PATTERN,
)
from agritechtz.logger import logger


class CropPricesPDFParser:
    """Class to extract text and convert data from PDFs into structured data (DataFrame)."""

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts text from all pages in a PDF file.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Combined text content of the PDF.
        """
        pdf_reader = PdfReader(pdf_path)
        text = "".join(page.extract_text() for page in pdf_reader.pages)
        return text

    def parse_dataframe(
        self, downloaded_file_path: str, source_file_path: str
    ) -> pd.DataFrame:
        """Converts text from PDF into a DataFrame using predefined regex patterns.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            pd.DataFrame: Structured data with each row representing a region's crop prices.
        """
        corpus = self.extract_text_from_pdf(downloaded_file_path)
        rows = REGIONAL_PATTERN.findall(corpus)
        df = pd.DataFrame(rows, columns=CROPS_COLUMNS)

        # Extract and add the date column from the PDF content
        date = self._extract_date_from_file_path(source_file_path)
        print(date)
        df.insert(0, "Date", pd.to_datetime(date, dayfirst=True, format="%d %B %Y"))

        # Convert numeric columns, handling missing values and commas
        min_max_columns = df.columns[df.columns.str.contains("Min|Max")]
        df[min_max_columns] = (
            df[min_max_columns]
            .replace({"NA": np.nan, ",": ""}, regex=True)
            .apply(pd.to_numeric, errors="coerce")
        )

        return df

    def _extract_date_from_file_path(self, file_path: str) -> str:
        logger.debug(file_path)

        # Define possible date patterns to search
        patterns = [DATE_PATTERN, DATE_PATTERN_WITH_MONTH_FIRST]

        for pattern in patterns:
            date_match = pattern.search(file_path)
            if date_match:
                # Determine day, month, and year order based on matched groups
                if len(date_match.groups()) == 3:
                    first, second, year = date_match.groups()
                    day, month = (
                        (first, second) if pattern == DATE_PATTERN else (second, first)
                    )
                    return f"{day} {self._standardize_month(month)} {year}"

        raise ValueError("Date not found in the PDF corpus.")

    def _standardize_month(self, month: str) -> str:
        replacements = {
            r"\bAgosti\b": "August",
            r"\bMachi\b": "March",
            r"\bJan\b": "January",
            r"\bFeb\b": "February",
            r"\bMar\b": "March",
            r"\bApr\b": "April",
            r"\bJun\b": "June",
            r"\bJul\b": "July",
            r"\bAug\b": "August",
            r"\bSept\b": "September",
            r"\bOct\b": "October",
            r"\bNov\b": "November",
            r"\bDec\b": "December",
            r"\bCtober\b": "October",
            r"\bSeptemba\b": "September",
        }
        for pattern, replacement in replacements.items():
            month = re.sub(pattern, replacement, month, flags=re.IGNORECASE)
        return month.title()


class Paginator:
    """Utility for identifying and retrieving PDF links across multiple pages."""

    def __init__(self, base_url: str, start_page=1):
        """Initialize Paginator with base URL"""
        self.base_url = base_url
        self.current_page = start_page
        self.start_page = start_page
        self.total_pages = None  # Will be computed by the compute_total_pages() method

    async def compute_total_pages(self) -> int:
        """
        Calculates the total number of pages with PDF links.

        Args:
            base_url (str): Base URL for page navigation.
            start_page (int): Starting page number to begin navigation.
        """
        current_page = self.current_page

        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    f"{self.base_url}?page={current_page}", timeout=500
                )
                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.find_all("a", href=True)

                # Get next page
                next_page = self.get_next_page(current_page, links)
                if not next_page:
                    break
                current_page = next_page
            self.total_pages = current_page
        return self.total_pages

    def filter_pdf_links(self, page_links: List[dict]) -> List[str]:
        """Filters and returns PDF links from HTML anchor elements.

        Args:
            page_links (List[dict]): List of links on a page.

        Returns:
            List[str]: Filtered PDF links.
        """
        pdf_links = [
            match[0]
            for link in page_links
            if (match := PDF_PATTERN.findall(link["href"]))
        ]
        return pdf_links

    def get_next_page(self, current_page: int, page_links: List[dict]) -> int | None:
        """Finds and returns the next page number based on navigation patterns.

        Args:
            current_page (int): Current page number.
            page_links (List[dict]): List of links on a page.

        Returns:
            int | None: Next page number if found; otherwise, None.
        """
        nav_links = [
            int(match[0][1])
            for link in page_links
            if (match := PAGES_PATTERN.findall(link["href"]))
        ]
        # Select the smallest page number greater than the current page
        next_page = min((pg for pg in nav_links if pg > current_page), default=None)
        return next_page

    def __aiter__(self):
        """Make paginator iterable"""
        # Reset to the start_page each time iteration begins
        self.current_page = self.start_page
        return self

    async def __anext__(self):
        """Asynchronous next method for iterating through pages and PDF links"""
        if self.total_pages is None:
            await self.compute_total_pages()
        if self.current_page > self.total_pages:
            raise StopAsyncIteration
        current_url = f"{self.base_url}?page={self.current_page}"
        self.current_page += 1
        return current_url


@asynccontextmanager
async def downloaded_pdf(pdf_url: str):
    """
    Asynchronous context manager for downloading a PDF into a temporary file
    and dispose it automatically
    """

    async with httpx.AsyncClient() as client:
        logger.info("Downloading PDF from %s", pdf_url)
        response = await client.get(pdf_url, timeout=500)

        # Create a temporary file for storing the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(temp_file.name, "wb") as fh:
            fh.write(response.content)

        try:
            # Yield the temp file for storing PDF
            yield temp_file.name
        finally:
            # Cleanup: Delete the temporary file after usage
            logger.info("Deleting temporary file: %s", temp_file.name)
            temp_file.close()
            os.remove(temp_file.name)


async def parsed_dataframes_stream(
    parser: CropPricesPDFParser, base_url: str, skip_urls: Set[str] | None = None
) -> AsyncGenerator[Tuple[str, pd.DataFrame], None]:
    """
    Asynchronous context manager for downloading multiple PDFs and extract data
    """

    paginator = Paginator(base_url=base_url)

    async with httpx.AsyncClient() as client:
        async for page in paginator:
            response = await client.get(page)
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)

            # Filter PDF links from the page
            pdf_links = paginator.filter_pdf_links(links)

            for url, filename in pdf_links:
                pdf_url = urllib.parse.quote(f"{url}{filename}", safe=":/,")
                if (skip_urls) and (pdf_url in skip_urls):
                    logger.info("URL %s already downloaded, skipping.", pdf_url)
                    continue
                async with downloaded_pdf(pdf_url) as pdf_file:
                    # Extract content
                    df = parser.parse_dataframe(
                        downloaded_file_path=pdf_file, source_file_path=filename
                    )
                    yield pdf_url, df
