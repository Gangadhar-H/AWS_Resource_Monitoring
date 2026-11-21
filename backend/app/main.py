from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import inventory, resources, scan, summary

app = FastAPI(title="Cloud Cost Monitor API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "provider": settings.cloud_provider, "region": settings.aws_region}


app.include_router(scan.router, prefix="/api")
app.include_router(resources.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
