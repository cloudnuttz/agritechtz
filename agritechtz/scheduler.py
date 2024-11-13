"""A module for scheduling tasks to be performed periodically"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from agritechtz.constants import BASE_URL
from agritechtz.database import acquire_session
from agritechtz.streamed_scrapper import CropPricesPDFParser
from agritechtz.workers import download_daily_updates


async def daily_updates_job():
    """Check daily updates from the Viwanda data and download into the database."""

    async with acquire_session() as session:
        parser = CropPricesPDFParser()
        base_url = BASE_URL

        await download_daily_updates(base_url=base_url, session=session, parser=parser)


def main():
    """Entry point for the schedulers"""

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # Set the new event loop

        scheduler = AsyncIOScheduler()
        # Runs daily at midnight
        scheduler.add_job(daily_updates_job, "cron", minute=0)

        # Start the scheduler
        scheduler.start()

        # Run the daily update job immediately (after scheduler starts)
        loop.run_until_complete(daily_updates_job())  # Execute the job immediately

        # Let the scheduler keep running indefinitely
        loop.run_forever()

    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
