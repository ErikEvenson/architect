import signal
import sys

import structlog
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.adrs import router as adrs_router
from src.api.artifacts import router as artifacts_router
from src.api.clients import router as clients_router
from src.api.coverage import router as coverage_router
from src.api.inventory import router as inventory_router
from src.api.uploads import router as uploads_router
from src.api.projects import router as projects_router
from src.api.questions import router as questions_router
from src.api.knowledge import router as knowledge_router
from src.api.rendering import router as rendering_router
from src.api.templates import router as templates_router
from src.api.versions import router as versions_router
from src.config import settings
from src.database import get_session

logger = structlog.get_logger()

API_V1_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Architect API",
        description="Cloud architecture design tool",
        version=settings.version,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health endpoints (outside API prefix)
    @app.get("/health/live")
    async def liveness():
        return {"status": "ok"}

    @app.get("/health/ready")
    async def readiness(session: AsyncSession = Depends(get_session)):
        from sqlalchemy import text

        try:
            await session.execute(text("SELECT 1"))
            return {"status": "ok"}
        except Exception:
            return JSONResponse(status_code=503, content={"status": "unavailable"})

    # API v1 routers
    app.include_router(clients_router, prefix=API_V1_PREFIX)
    app.include_router(projects_router, prefix=API_V1_PREFIX)
    app.include_router(versions_router, prefix=API_V1_PREFIX)
    app.include_router(artifacts_router, prefix=API_V1_PREFIX)
    app.include_router(adrs_router, prefix=API_V1_PREFIX)
    app.include_router(questions_router, prefix=API_V1_PREFIX)
    app.include_router(rendering_router, prefix=API_V1_PREFIX)
    app.include_router(templates_router, prefix=API_V1_PREFIX)
    app.include_router(knowledge_router, prefix=API_V1_PREFIX)
    app.include_router(coverage_router, prefix=API_V1_PREFIX)
    app.include_router(inventory_router, prefix=API_V1_PREFIX)
    app.include_router(uploads_router, prefix=API_V1_PREFIX)

    return app


app = create_app()


def handle_signal(signum, frame):
    logger.info("received_signal", signal=signal.Signals(signum).name)
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
