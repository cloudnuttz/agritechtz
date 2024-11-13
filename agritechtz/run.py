"""A module to test daily execution"""

import asyncio

import agritechtz.database as db
from agritechtz.constants import BASE_URL
from agritechtz.streamed_scrapper import CropPricesPDFParser
from agritechtz.workers import download_daily_updates


async def main():
    """Entry point"""

    # Initialize the database (if needed)
    await db.init_db()

    # Start a session and run the download task
    async with db.acquire_session() as session:
        await download_daily_updates(
            session=session, parser=CropPricesPDFParser(), base_url=BASE_URL
        )


if __name__ == "__main__":

    asyncio.run(main())
