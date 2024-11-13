"""Entrypoint for the application"""

from fastapi import FastAPI, Request, Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from agritechtz.api.v1.crops import router
from agritechtz.database import acquire_session
from agritechtz.logger import logger
from agritechtz.security import limiter

app = FastAPI()


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def database_middleware(request: Request, call_next):
    """Initialize middleware"""
    response = Response(status_code=500)
    async with acquire_session() as session:
        try:
            request.state.session = session
            response = await call_next(request)
        finally:
            logger.info("Finished processing")
        return response


app.include_router(router, prefix="/api/v1/crop-prices")
