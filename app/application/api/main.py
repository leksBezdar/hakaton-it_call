from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from application.api.lifespan import (
    close_message_broker,
    close_scheduler,
    init_message_broker,
    init_scheduler,
)

from application.api.healthcheck import healthcheck_router
from application.api.users.routers import user_router
from application.api.users.routers import auth_router
from settings.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_message_broker()
    await init_scheduler()
    yield
    await close_scheduler()
    await close_message_broker()


def create_app() -> FastAPI:
    app = FastAPI(
        title="hakaton it-call",
        description="They have my IP address? How do they know where I pee?",
        debug=True,
        lifespan=lifespan,
    )

    app.include_router(auth_router, prefix="/auth", tags=["AUTH"])
    app.include_router(user_router, prefix="/users", tags=["USERS"])
    app.include_router(healthcheck_router, prefix="/healthcheck", tags=["HEALTHCHECK"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_CORS_ORIGINS,
        allow_origin_regex=settings.ALLOWED_CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
