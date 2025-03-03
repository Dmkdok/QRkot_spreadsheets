import logging

from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.core.init_db import create_first_superuser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    docs_url='/swagger',
    redoc_url='/redoc',
)

app.include_router(main_router)


@app.on_event('startup')
async def startup():
    await create_first_superuser()
