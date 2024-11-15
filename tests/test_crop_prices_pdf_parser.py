"""The unit testing module for the crop prices pdf parser function"""

from urllib.parse import quote
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from pytest_mock import MockFixture
import pandas as pd


from agritechtz.constants import BASE_URL, REGIONAL_PATTERN
from agritechtz.streamed_scrapper import CropPricesPDFParser, parsed_dataframes_stream


class MockPage:
    """Mock class to simulate a PDF page with text extraction functionality."""

    def __init__(self, text):
        self._text = text

    def extract_text(self):
        """Simulates text extraction from a PDF page."""
        return self._text


def test_clean_region():
    """Test the logic to clean regions"""

    parser = CropPricesPDFParser()

    region = "Dar es saalam"
    expected = ["Dar-es-Salaam"]

    actual = parser.standardize_region(region, expected)

    assert actual == expected[0]


def test_standardize_region_no_match():
    """Test that standardize_region raises an error if no match is found."""
    parser = CropPricesPDFParser()

    region = "Unknown"

    try:
        parser.standardize_region(region, ["Mbeya", "Dar-es-Salaam", "Dodoma"])
    except ValueError as e:
        assert str(e) == "Could not find region: Unknown from the list."


def test_match_and_clean_text():
    """Test text matching and cleaning from extracted PDF content."""
    parser = CropPricesPDFParser()

    text = "Mbeya Soweto 100 200 NA NA NA 300 400 500 600 900 NA NA NA NA 200 300"
    rows = parser.match_and_clean_text(text, REGIONAL_PATTERN)

    assert rows == [
        (
            "Mbeya",
            "Soweto",
            "100",
            "200",
            "NA",
            "NA",
            "NA",
            "300",
            "400",
            "500",
            "600",
            "900",
            "NA",
            "NA",
            "NA",
            "NA",
            "200",
            "300",
        )
    ]


def test_extract_text_from_pdf():
    """Test the extract_text_from_pdf function with mocked PDF pages."""

    # Create a mock for the PdfReader
    with patch(
        "agritechtz.streamed_scrapper.PdfReader"
    ) as MockPdfReader:  # pylint: disable=invalid-name
        # Mock the pages with extract_text method returning sample text
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 text"

        # Set up the PdfReader mock to have pages attribute
        MockPdfReader.return_value.pages = [mock_page1, mock_page2]

        # Instantiate parser and call extract_text_from_pdf
        parser = CropPricesPDFParser()
        result_text = parser.extract_text_from_pdf("dummy_path.pdf")

        # Verify that the combined text is as expected
        assert result_text == "Page 1 textPage 2 text"


def test_standardize_month():
    """Test standardize_month for various month name variations."""
    parser = CropPricesPDFParser()

    months = [
        ("Agosti", "August"),
        ("Machi", "March"),
        ("Jan", "January"),
        ("Jul", "July"),
        ("Nov", "November"),
        ("Ctober", "October"),
        ("Septemba", "September"),
    ]

    for month, expected in months:
        actual = parser.standardize_month(month)
        assert actual == expected


def test_parse_dataframe():
    """Test converting extracted PDF text to DataFrame."""
    parser = CropPricesPDFParser()

    # Mock data extraction methods
    parser.extract_text_from_pdf = (
        lambda _: "Mbeya Songwe 100 200 300 200 350 240 350 200 300 320 NA NA 789 800 NA NA"
    )
    parser.match_and_clean_text = lambda text, _: [
        (
            "Mbeya",
            "Songwe",
            "100",
            "200",
            "300",
            "200",
            "350",
            "240",
            "350",
            "200",
            "300",
            "320",
            "NA",
            "NA",
            "789",
            "800",
            "NA",
            "NA",
        )
    ]
    parser.extract_date_from_file_path = lambda _: "01 January 2023"

    df = parser.parse_dataframe("dummy_path.pdf", "dummy_file.pdf")

    assert isinstance(df, pd.DataFrame)
    assert df.loc[0, "Region"] == "Mbeya"
    assert df.loc[0, "Maize Min"] == 100
    assert (
        pd.to_datetime(df.loc[0, "Date"]).date() == pd.to_datetime("2023-01-01").date()
    )


@pytest.mark.asyncio
async def test_parsed_dataframes_stream(mocker: MockFixture):
    """Test downloading, parsing, and streaming of DataFrames from PDF links."""

    # Create the mock objects
    mock_paginator = mocker.patch(
        "agritechtz.streamed_scrapper.Paginator", autospec=True
    )
    mock_paginator_instance = mock_paginator.return_value
    mock_paginator_instance.__aiter__.return_value = iter([f"{BASE_URL}?page=1"])
    mock_response = AsyncMock()
    mock_response.text = (
        f"<html>"
        f"<a href='{BASE_URL}/sw-0000000000-Wholesale-Jan 2 2024.pdf'></a>"
        f"</html>"
    )
    mock_paginator_instance.filter_pdf_links.return_value = [
        (BASE_URL, "/sw-0000000000-Wholesale-Jan 2 2024.pdf")
    ]

    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=mock_response)
    mock_downloaded_pdf = mocker.patch(
        "agritechtz.streamed_scrapper.downloaded_pdf", return_value=AsyncMock()
    )
    mock_pdf_file = mock_downloaded_pdf.return_value.__aenter__.return_value
    mock_pdf_file.name = "some-downloaded-pdf-file.pdf"

    # Mocking parser to avoid actual PDF parsing
    mock_parser = MagicMock(spec=CropPricesPDFParser)
    mock_parser.parse_dataframe.return_value = pd.DataFrame(
        [
            {
                "ts": pd.Timestamp("2024-01-01"),
                "region": "Mbeya",
                "district": "Mbeya",
                "Maize Min": 40000,
                "Maize Max": 50000,
            }
        ]
    )

    async for url, _ in parsed_dataframes_stream(mock_parser, BASE_URL):
        assert url == f"{BASE_URL}/{quote('sw-0000000000-Wholesale-Jan 2 2024.pdf')}"

    # Verify the mock was called with expected arguments
    mock_get.assert_called_with(f"{BASE_URL}?page=1")
    # mock_parser.parse_dataframe.assert_called_with(
    #     downloaded_file_path="some-downloaded-pdf-file.pdf",
    #     source_file_path="/sw-0000000000-Wholesale-Jan 2 2024.pdf",
    # )


# @pytest.mark.asyncio
# async def test_parsed_dataframes_stream_skip_urls():
#     """Test that parsed_dataframes_stream skips already downloaded URLs."""
#     parser = CropPricesPDFParser()
#     parser.parse_dataframe = AsyncMock(return_value=pd.DataFrame({"Region": ["Mbeya"]}))

#     skip_urls = {
#         f"{BASE_URL}/sw-0000000000-Wholesale-Jan 2 2024.pdf",
#         f"{BASE_URL}/sw-2222222222-Wholesale-Jan 4 2024.pdf",
#     }

#     async for url, df in parsed_dataframes_stream(
#         parser, BASE_URL, skip_urls=skip_urls
#     ):
#         assert url not in skip_urls  # Ensure skipped URLs are not processed
#         assert not df.empty
