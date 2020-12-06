from fastapi import FastAPI

from distribution.router import distribution_router

app = FastAPI(title="Music Distributions", version="20.12.0")

app.include_router(distribution_router, prefix="/distributions")
