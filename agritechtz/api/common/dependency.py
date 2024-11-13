"""Dependencies module for the API endpoints"""

from agritechtz.repository import CropPricesRepository

from fastapi import Request


def crop_prices_repository(request: Request):
    """Factory function for the repository used to manage prices repository"""
    session = request.state.session

    return CropPricesRepository(session)
