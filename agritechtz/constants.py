"""Applicable constants across the codebase"""

import re

# Constants
CROPS_COLUMNS = [
    "Region",
    "District",
    "Maize Min",
    "Maize Max",
    "Rice Min",
    "Rice Max",
    "Sorghum Millet Min",
    "Sorghum Millet Max",
    "Bulrush Millet Min",
    "Bulrush Millet Max",
    "Finger Millet Min",
    "Finger Millet Max",
    "Wheat Min",
    "Wheat Max",
    "Beans Min",
    "Beans Max",
    "Irish Potato Min",
    "Irish Potato Max",
]

# Base URL where the crops are available
BASE_URL = "https://www.viwanda.go.tz/documents/product-prices-domestic"

# Regex patterns for extracting information
PDF_PATTERN = re.compile(
    r"(https://www.viwanda.go.tz/uploads/documents/)(sw-\d{10}-Wholesale.+?.pdf)",
    re.IGNORECASE,
)

PAGES_PATTERN = re.compile(r"\?page=(\d+)")

TZ_REGIONS = [
    "Arusha",
    "Dar-es-Salaam",
    "Dodoma",
    "Geita",
    "Iringa",
    "Kagera",
    "Katavi",
    "Kigoma",
    "Kilimanjaro",
    "Lindi",
    "Manyara",
    "Mara",
    "Mbeya",
    "Mjini Magharibi",
    "Morogoro",
    "Mtwara",
    "Mwanza",
    "Njombe",
    "Pemba Kaskazini",
    "Pemba Kusini",
    "Pwani",
    "Rukwa",
    "Ruvuma",
    "Shinyanga",
    "Simiyu",
    "Singinda",
    "Songwe",
    "Tabora",
    "Tanga",
    "Unguja Kaskazini",
    "Unguja Kusini",
]

REGIONAL_PATTERN = re.compile(
    r"(Dar es salaam|Dar es saalam|Kilimanjaro|Singida|Arusha|Dodoma|Morogoro|Mtwara|Lindi|Iringa"
    r"|Mara|Tanga|Songwe|Tabora|Geita|Kagera|Katavi|Manyara|Mbeya|Shinyanga|Ruvuma|Mwanza|Pwani"
    r"|Simiyu|Kigoma|Rukwa|Njombe)"
    r"\s+([\w\s\/]+?)"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))"
    r"(?:\s+(NA|\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?))",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

DATE_PATTERN = re.compile(
    r"(\d{1,2})(?:\s*)(?:_|.)?(?:st|nd|rd|th)?(?:_|.)?(?:\s)*?(?:of\s*)?"
    r"(january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec|januari|februari|machi|aprili|mei|juni|"
    r"julai|agosti|septemba|novemba|desemba)(?:\s+)?(?:,\s?)?(?:_|.)?(\d{4})",
    re.IGNORECASE,
)

DATE_PATTERN_WITH_MONTH_FIRST = re.compile(
    r"(january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sept|oct|nov|dec|januari|februari|machi|aprili|mei|juni|"
    r"julai|agosti|septemba|novemba|desemba)(?:\s*)+?"
    r"(\d{1,2})(?:\s*)(?:st|nd|rd|th)?(?:\s*)+?(\d{4})",
    re.IGNORECASE,
)
