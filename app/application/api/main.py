from fastapi import FastAPI

from application.api.healthcheck import healthcheck_router
from application.api.users.routers import user_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="hakaton it-call",
        description="They have my IP address? How do they know where I pee?",
        debug=True,
    )

    app.include_router(healthcheck_router, prefix="/healthcheck", tags=["HEALTHCHECK"])
    app.include_router(user_router, prefix="/users", tags=["USERS"])

    return app
