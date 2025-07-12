from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.logger_config import config_logger
from app.routes import auth, book, cart, orders, roles, shipping_cost, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        config_logger.info("🚀App is starting up...")

    except Exception as e:
        config_logger.exception(f"❌ Error in the startup stage: {e}")

    yield


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

f_api.include_router(auth.user_router)
f_api.include_router(auth.login_router)
f_api.include_router(users.user_router)
f_api.include_router(roles.roles_router)
f_api.include_router(book.book_router)
f_api.include_router(shipping_cost.shipping_router)
f_api.include_router(cart.cart_router)
f_api.include_router(orders.order_router)
