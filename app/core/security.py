from datetime import datetime, timedelta
from typing import Optional
import logging
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlmodel import Session,select
from app.core.config import settings
from app.db.database import get_session 
from app.models.models import User
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Request
from app.models.models import user as user_crud
from sqlmodel.ext.asyncio.session import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# URL-safe token serializer (for emails, etc.)
serializer = URLSafeTimedSerializer(
    secret_key=settings.SECRET_KEY,
    salt="email-configuration"
)

def create_url_safe_token(data: dict) -> str:
    """
    Create a URL-safe token for sending in links (e.g. email verification).
    """
    return serializer.dumps(data)

def decode_url_safe_token(token: str) -> dict | None:
    """
    Decode a URL-safe token. Returns the original data or None if invalid.
    """
    try:
        return serializer.loads(token)
    except (BadSignature, SignatureExpired) as e:
        logging.error(f"Invalid or expired URL-safe token: {e}")
        return None



def decode_token(token: str) -> dict | None:
    """Verify a JWT token and return its payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logging.error(f"Invalid token: {e}")
        return None

def verify_token(token: str) -> dict | None:
    """Verify a JWT token and return its payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logging.error(f"Invalid token: {e}")
        return None


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials

        token_data = decode_token(token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please override this method in a child class")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data.get("refresh"):
            raise HTTPException(status_code=401, detail="Access token required")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data.get("refresh"):
            raise HTTPException(status_code=401, detail="Refresh token required")

async def get_current_user(
    db: AsyncSession = Depends(get_session), token: dict = Depends(AccessTokenBearer())
) :
          email = token.get["email"]
          
          result = await db.exec(select(User).where(User.email == email))
          user = result.first()
          return user

access_token_bearer = AccessTokenBearer()