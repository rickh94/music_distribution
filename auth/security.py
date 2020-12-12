import os
import urllib.error

from deta import Deta
from fastapi import HTTPException, Security, Depends
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from python_jam import JustAuthenticateMe, JAMNotVerified
from starlette.requests import Request

from auth import models

ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS").lower().split(",")
WHITELIST = os.getenv("WHITELIST").lower().split(",")
JAM = JustAuthenticateMe(os.getenv("JAM_APP_ID"))


class JAMAuthentication(OAuth2):
    def __init__(
        self,
        *args,
        tokenUrl: str,
        authorizationUrl: str,
        token_name: str = "token",
        refresh_token_name: str = "refresh_token",
        **kwargs
    ):
        flows = OAuthFlows(
            authorizationCode={
                "tokenUrl": tokenUrl,
                "authorizationUrl": authorizationUrl,
            }
        )
        super().__init__(flows=flows, *args, **kwargs)
        self.token_name = token_name
        self.refresh_token_name = refresh_token_name

    async def __call__(self, request: Request) -> str:
        """Extract token from cookies"""
        token = request.cookies.get(self.token_name)
        if not token:
            raise HTTPException(status_code=401, detail="Not Authorized")
        return token


def validate_email(email) -> bool:
    domain = email.split("@")[-1]
    if domain.lower() in ALLOWED_DOMAINS or email in WHITELIST:
        return True
    return False


oauth2_scheme = JAMAuthentication(
    tokenUrl="/auth/confirm", authorizationUrl="/auth/request"
)


async def get_current_user(token: str = Security(oauth2_scheme)) -> models.User:
    credential_exception = HTTPException(status_code=401, detail="Invalid Token")
    try:
        headers, claims = await JAM.verify_token(token)
    except JAMNotVerified as e:
        if str(e) == "expired":
            raise HTTPException(status_code=401, detail="Expired Token")
        raise credential_exception
    email = claims.get("email")
    if not email:
        raise credential_exception
    # deta = Deta(os.getenv('PROJECT_KEY'))
    # users = deta.Base('user')
    # user = next(users.fetch({"email": email}))
    # user = user[0]
    user = await models.get_user_by_email(email)
    if not user:
        user = await models.create_user_from_email(email)
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="User is disabled")
    return current_user
