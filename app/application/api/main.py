from fastapi import FastAPI

from application.api.healthcheck import healthcheck_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="hakaton it-call",
        description="They have my IP address? How do they know where I pee?!",
        debug=True,
    )

    app.include_router(healthcheck_router, prefix="/healthcheck", tags=["HEALTHCHECK"])

    return app
