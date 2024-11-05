from typing import Generator
from .database import SessionLocal
from fastapi import HTTPException, Depends
from firebase_admin import auth as firebase_auth
from .models.user import User

def get_db() -> Generator:
    """
    Dependency for getting database session.
    Ensures proper handling of database connections and error cases.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token.
    Raises HTTPException if token is invalid.
    """
    try:
        return firebase_auth.verify_id_token(token)
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail={"detail": "Invalid token", "code": "INVALID_TOKEN"}
        )
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401,
            detail={"detail": "Token expired", "code": "TOKEN_EXPIRED"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={"detail": str(e), "code": "TOKEN_VERIFICATION_FAILED"}
        )

async def get_current_user(
    token: str,
    db: SessionLocal = Depends(get_db)
) -> User:
    """
    Dependency for getting current authenticated user.
    Verifies token and returns corresponding user from database.
    """
    decoded_token = await verify_firebase_token(token)
    user = db.query(User).filter(User.firebase_uid == decoded_token['uid']).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"detail": "User not found", "code": "USER_NOT_FOUND"}
        )
    
    return user
