"""Data repository module"""

from typing import List

from sqlalchemy import and_, any_, column, func, true
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import lateral

from agritechtz.models import CropPrice
from agritechtz.api.v1.schema import CropPricesFilter


class CropPricesRepository:
    """Repository class for accessing and filtering crop prices"""

    def __init__(self, session: AsyncSession):
        """Initialize the CropPrices data repository."""
        self.session = session

    async def filter_prices(
        self, crop_prices_filter: CropPricesFilter
    ) -> List[CropPrice]:
        """Filter crop prices from the repository using CropPricesFilter.

        Args:
            filter (CropPricesFilter): Filter instance containing filtering criteria.

        Returns:
            List[CropPrice]: A list of filtered CropPrice records.
        """
        query = select(CropPrice)

        if crop_prices_filter.crop_prices__in:
            # Alias the table
            cp = CropPrice.__table__.alias("cp")

            # Define the lateral function with proper aliasing
            elem = lateral(
                func.json_array_elements(cp.c.crop_prices)
                .table_valued(column("value", JSON))
                .alias("elem")
            )
            patterns = [f"%{crop}" for crop in crop_prices_filter.crop_prices__in]

            # Apply the conditions
            subquery = (
                select(
                    cp.c.source_url.label("source_url"),
                    cp.c.ts.label("ts"),
                    cp.c.region.label("region"),
                    cp.c.district.label("district"),
                    func.jsonb_agg(elem.c.value).label("crop_prices"),
                )
                .select_from(cp.join(elem, true()))
                .where(elem.c.value["name"].astext.ilike(any_(patterns)))
                .group_by(cp.c.source_url, cp.c.ts, cp.c.region, cp.c.district)
                .subquery()
            )

            query = select(
                CropPrice.source_url,
                CropPrice.ts,
                CropPrice.region,
                CropPrice.district,
                subquery.c.crop_prices,
            ).join(
                subquery,
                and_(
                    CropPrice.source_url == subquery.c.source_url,
                    CropPrice.ts == subquery.c.ts,
                    CropPrice.region == subquery.c.region,
                    CropPrice.district == subquery.c.district,
                ),
            )

            # Clear the crop_prices__crop_in filter to prevent re-application
            crop_prices_filter.crop_prices__in = None

        # Apply filter criteria to query
        query = crop_prices_filter.filter(query)  # Apply filter criteria to query

        # Apply order
        query = crop_prices_filter.sort(query)

        result = await self.session.execute(query)
        return result.all()
