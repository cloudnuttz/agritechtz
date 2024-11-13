"""API endpoints module for the crops"""

import csv
from io import StringIO
from fastapi import APIRouter, Depends, Response
from fastapi_filter import FilterDepends

from agritechtz.api.common.dependency import crop_prices_repository
from agritechtz.api.v1.schema import CropPricesFilter
from agritechtz.repository import CropPricesRepository

router = APIRouter()


@router.get("/")
async def filter_prices_crops(
    repository: CropPricesRepository = Depends(crop_prices_repository),
    crop_prices_filter: CropPricesFilter = FilterDepends(CropPricesFilter),
):
    """Filter crop prises"""
    prices = await repository.filter_prices(crop_prices_filter)

    # Convert to CSV
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["ts", "region", "district", "crop", "min_price", "max_price"])

    # Write data rows
    for price in prices:
        print(price)
        for crop in price.crop_prices:
            writer.writerow(
                [
                    price.ts,
                    price.region,
                    price.district,
                    crop["name"],
                    crop["min"],
                    crop["max"],
                ]
            )
    # Prepare CSV response
    output.seek(0)
    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=crop_prices.csv"
    return response
