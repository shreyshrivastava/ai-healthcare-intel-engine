import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import drug_interaction, second_opinion, symptom_specialist


def allowed_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["*"]


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Healthcare Intelligence Engine",
        version="0.1.0",
        description="Symptom-to-specialist, second-opinion risk, and drug interaction intelligence APIs.",
    )

    origins = allowed_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials="*" not in origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        symptom_specialist.router,
        prefix="/symptom-specialist",
        tags=["symptom-specialist"],
    )
    app.include_router(second_opinion.router, prefix="/second-opinion", tags=["second-opinion"])
    app.include_router(
        drug_interaction.router,
        prefix="/drug-interactions",
        tags=["drug-interactions"],
    )

    @app.get("/")
    def root():
        return {
            "status": "ok",
            "message": "AI Healthcare Intelligence Engine API is running. Visit /docs for documentation.",
        }

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
