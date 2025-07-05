from contextlib import asynccontextmanager
from app.config.logger_config import config_logger
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        config_logger.info("🚀App is starting up...")

    except Exception as e:
        config_logger.exception(f"❌ Error in the startup stage: {e}")

    yield

    print("🙏 App shutting down...")


# App metadata
f_api = FastAPI(
    title="Online Book Store System",
    description="An online book store system built with FastAPI.",
    version="1.0.0",
    contact={
        "name": "Monocept Team",
        "url": "https://github.com/Himanshu0273/Book_Store_FastAPI",
        "email": "baidheman14@gmail.com",
    },
    lifespan=lifespan,
)

