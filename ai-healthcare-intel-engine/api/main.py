from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import symptom_specialist, second_opinion, drug_interaction


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Healthcare Intelligence Engine",
        version="0.1.0",
        description="Symptom-to-specialist, second-opinion risk, and drug interaction intelligence APIs.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(symptom_specialist.router, prefix="/symptom-specialist", tags=["symptom-specialist"])
    app.include_router(second_opinion.router, prefix="/second-opinion", tags=["second-opinion"])
    app.include_router(drug_interaction.router, prefix="/drug-interactions", tags=["drug-interactions"])

    @app.get("/")
    def root():
        return {"status": "ok", "message": "AI Healthcare Intelligence Engine API is running. Visit /docs for documentation."}

    return app


app = create_app()
