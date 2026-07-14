from fastapi import FastAPI
from mangum import Mangum

from routers import employees, departments, jobs
app = FastAPI(
    title="Globant Data Engineering Challenge API",
    description="REST API for historical data migration, validation, backup/restore, and SQL reporting.",
    version="0.2.0",
)

app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(jobs.router)


@app.get("/", tags=["Root"])
def read_root() -> dict:
    return {"service": "globant-de-challenge-api", "status": "running"}


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok"}


handler = Mangum(app)