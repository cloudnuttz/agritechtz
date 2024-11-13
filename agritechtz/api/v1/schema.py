"""Schema for data exchanging between clients and the service"""

from datetime import date
from decimal import Decimal
from typing import List
from agritechtz.models import CropPrice
from fastapi_filter.contrib.sqlalchemy import Filter


class CropPricesFilter(Filter):
    """Filter schema class for the crop prices."""

    region__in: List[str] | None = None
    district__in: List[str] | None = None
    crop_prices__in: List[str] | None = None
    ts__gte: date | None = None
    ts__lte: date | None = None
    price__min__gte: Decimal | None = None
    price__max__gte: Decimal | None = None

    ordering: List[str] = ["+ts"]

    class Constants:
        """Filters configurations."""

        ordering_field_name = "ordering"
        search_field_name = "crop"  # Define the field name for searches
        model = CropPrice  # This references the model to filter against
