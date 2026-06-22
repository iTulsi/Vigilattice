from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vigilattice import __version__
from vigilattice.api.router import api_router
from vigilattice.core.config import get_settings
from vigilattice.core.logging import configure_logging
from vigilattice.services.container import get_arena_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    get_arena_service().load_scenarios()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Vigilattice API",
        version=__version__,
        description="Adversarial evaluation infrastructure for autonomous AI agents.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
