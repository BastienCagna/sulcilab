import time
from sqlalchemy.orm import Session
from sulcilab.core import crud
from fastapi import Depends

import jwt
from decouple import config

from sulcilab.core.jwt import PJWT

import typing
if typing.TYPE_CHECKING:
    from sulcilab.core.user import User, PUser

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token: str):
    return {
        "token": token
    }

def signJWT(user: 'PUser') -> PJWT:#Dict[str, str]:
    payload = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "expiration": time.time() + 3600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expiration"] >= time.time() else None
    except:
        return {}
