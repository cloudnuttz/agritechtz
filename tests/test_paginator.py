"""Unittesting module to assess the functionality of pagination logic"""

from agritechtz.streamed_scrapper import Paginator


BASE_URL = "https://www.viwanda.go.tz/uploads/documents"


def test_paginator_get_next_page():
    """Test getting the next page from a list of page links."""
    paginator = Paginator(base_url=f"{BASE_URL}")

    links = [{"href": "?page=2"}, {"href": "?page=3"}]
    assert paginator.get_next_page(1, links) == 2
    assert paginator.get_next_page(2, links) == 3


def test_filter_pdf_links():
    """Test that filter_pdf_links correctly filters out non-PDF links."""
    paginator = Paginator(base_url=BASE_URL)

    links = [
        {"href": f"{BASE_URL}/sw-0000000000-Wholesale-Jan 2 2024.pdf"},
        {"href": f"{BASE_URL}/sw-1111111111-Wholesale-Jan 3 2024.txt"},
        {"href": f"{BASE_URL}/sw-2222222222-Wholesale-Jan 4 2024.pdf"},
    ]

    pdf_links = paginator.filter_pdf_links(links)

    assert len(pdf_links) == 2
    assert "sw-0000000000-Wholesale-Jan 2 2024.pdf" == pdf_links[0][1]
    assert "sw-2222222222-Wholesale-Jan 4 2024.pdf" == pdf_links[1][1]


def test_paginator_empty_page():
    """Test that paginator stops when no next page is found."""
    paginator = Paginator(base_url=BASE_URL)

    links = [{"href": "?page=1"}]  # Assume the only available page is page 1
    assert paginator.get_next_page(1, links) is None
