from typing import List, Optional
import urllib.error

import odetam.exceptions
from fastapi import APIRouter, HTTPException, Depends

from auth.models import User
from auth.security import get_current_active_user
from distribution import models

distribution_router = APIRouter()


@distribution_router.post("/", response_model=models.MusicDistribution)
async def create_distribution(distribution: models.MusicDistribution):
    distribution.save()
    return distribution


@distribution_router.get("/")
def get_all_distributions(_current_user: User = Depends(get_current_active_user)):
    try:
        return models.MusicDistribution.get_all()
    except urllib.error.HTTPError:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@distribution_router.post("/search", response_model=List[models.MusicDistribution])
def query_distributions_by_student(
    student: Optional[str], _current_user: User = Depends(get_current_active_user)
):
    return models.MusicDistribution.query(
        models.MusicDistribution.student.contains(student)
    )


@distribution_router.get("/{key}", response_model=models.MusicDistribution)
def get_distribution_by_key(
    key: str, _current_user: User = Depends(get_current_active_user)
):
    try:
        return models.MusicDistribution.get(key)
    except odetam.exceptions.ItemNotFound:
        raise HTTPException(status_code=404, detail="Item not found")


@distribution_router.put("/{key}", response_model=models.MusicDistribution)
def update_distribution(
    key: str,
    distribution: models.MusicDistribution,
    _current_user: User = Depends(get_current_active_user),
):
    if distribution.key is None:
        distribution.key = key
    elif distribution.key != key:
        raise HTTPException(status_code=400, detail="Path and item key do not match")
    distribution.save()
    return distribution


@distribution_router.delete("/{key}", status_code=204)
def delete_distribution(
    key: str, _current_user: User = Depends(get_current_active_user)
):
    models.MusicDistribution.delete_key(key)
