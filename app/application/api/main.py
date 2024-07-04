from contextlib import asynccontextmanager
from fastapi import FastAPI

from application.api.lifespan import (
    close_message_broker,
    init_message_broker,
)

from application.api.healthcheck import healthcheck_router
from application.api.users.routers import user_router
from application.api.users.routers import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_message_broker()
    yield
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

    return app
