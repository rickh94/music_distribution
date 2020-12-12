import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, Depends, Body
from python_jam import JAMBadRequest, JustAuthenticateMeError, JAMUnauthorized
from starlette.requests import Request

from auth import models, security
from auth.models import LoginRequest, UserUpdate
from auth.security import JAM, validate_email, oauth2_scheme

auth_router = APIRouter()


@auth_router.post("/request")
async def request(login_request: LoginRequest):
    if not validate_email(login_request.email):
        raise HTTPException(
            status_code=401, detail="You are not authorized to use this site."
        )
    try:
        await JAM.authenticate(login_request.email)
    except JAMBadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))
    except JustAuthenticateMeError:
        raise HTTPException(status_code=500, detail="Internal Error, try again later")
    return "success"


@auth_router.get("/confirm")
async def confirm(refreshToken: Optional[str], response: Response):
    new_id_token = await JAM.refresh(refreshToken)
    response.set_cookie(oauth2_scheme.token_name, new_id_token, httponly=True, secure=True)
    response.set_cookie(
        oauth2_scheme.refresh_token_name, refreshToken, httponly=True, secure=True
    )
    return {"status": "authenticated"}


@auth_router.get("/refresh")
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get(oauth2_scheme.refresh_token_name)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Please log in")
    try:
        id_token = await JAM.refresh(refresh_token)
    except JAMBadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))
    except JAMUnauthorized:
        raise HTTPException(status_code=401, detail="Please log in")
    except JustAuthenticateMeError:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    response.set_cookie(oauth2_scheme.token_name, id_token, httponly=True, secure=True)
    return {"status": "authenticated"}


@auth_router.get("/me", response_model=models.User)
async def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Get User Data"""
    return current_user


@auth_router.post("/me/update", response_model=models.UserUpdateResponse)
async def put_users_me(
    update: UserUpdate,
    response: Response,
    current_user: models.User = Depends(security.get_current_active_user),
):
    message = "updated"
    if update.name:
        current_user.name = update.name
    if update.email:
        message = "please log in again"
        response.set_cookie(oauth2_scheme.token_name, "")
        response.set_cookie(oauth2_scheme.refresh_token_name, "")
        current_user.email = update.email
    current_user.save()
    return models.UserUpdateResponse(message=message, user=current_user)
