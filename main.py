from fastapi import FastAPI

from auth.router import auth_router
from distribution.router import distribution_router

app = FastAPI(title="Music Distributions", version="20.12.1")

app.include_router(distribution_router, prefix="/distributions", tags=["distributions"])

app.include_router(auth_router, prefix="/auth", tags=["auth"])
