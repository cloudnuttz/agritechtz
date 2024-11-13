"""Module for the tasks"""

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agritechtz.logger import logger
from agritechtz.models import CropPrice
from agritechtz.utils import camel_to_snake
from agritechtz.streamed_scrapper import CropPricesPDFParser, parsed_dataframes_stream
from agritechtz.utils import sanitize_data


async def download_daily_updates(
    base_url: str,
    session: AsyncSession,
    parser: CropPricesPDFParser,
):
    """Download daily crop prices from the source and save to the database."""

    try:
        # Retrieve the last page downloaded
        # Retrieve all downloaded URLs to avoid re-downloading
        downloaded_urls_result = await session.execute(select(CropPrice.source_url))
        downloaded_urls = {url for url, in downloaded_urls_result.fetchall()}

        async for source_url, df in parsed_dataframes_stream(
            parser=parser, base_url=base_url, skip_urls=downloaded_urls
        ):

            df.columns = [camel_to_snake(column) for column in df.columns]
            df = df.rename(columns={"date": "ts"})
            if df.empty:
                logger.info("No new data to download.")
                continue

            logger.debug("DataFrame: %s", df)

            # `CropPrice` is the SQLAlchemy model with crop prices stored in a JSON field
            crop_price_instances = []

            for row in df.to_dict(orient="records"):
                # Prepare the `crop_prices` dictionary with crop data
                crop_prices = [
                    {
                        "name": crop,
                        "min": sanitize_data(row.get(f"{crop}_min", None)),
                        "max": sanitize_data(row.get(f"{crop}_max", None)),
                    }
                    for crop in [
                        "maize",
                        "rice",
                        "beans",
                        "sorghum_millet",
                        "bulrush_millet",
                        "finger_millet",
                        "wheat",
                        "irish_potato",
                    ]
                    if pd.notnull(row.get(f"{crop}_min"))
                    or pd.notnull(row.get(f"{crop}_max"))
                ]

                # Create an instance of `CropPrice` for each row
                crop_price_instance = CropPrice(
                    source_url=source_url,
                    ts=row["ts"],
                    region=row["region"],
                    district=row["district"],
                    crop_prices=crop_prices,
                )

                crop_price_instances.append(crop_price_instance)

            session.add_all(crop_price_instances)
            # Commit transaction
            await session.commit()

    except Exception as e:
        await session.rollback()
        logger.exception("An error occurred during the download and insert process.")
        raise e
