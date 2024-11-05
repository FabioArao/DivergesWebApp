from fastapi import APIRouter, Depends, HTTPException, Request
from firebase_admin import auth as firebase_auth
from firebase_admin.auth import InvalidIdTokenError, ExpiredIdTokenError
from ..dependencies import get_db
from ..models.user import User, UserRole
from ..schemas.auth import TokenSchema, UserResponse, ErrorResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..middleware.security import limiter
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, responses={400: {"model": ErrorResponse}})
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    token_schema: TokenSchema,
    db: Session = Depends(get_db)
):
    try:
        # Verify Firebase token
        try:
            decoded_token = firebase_auth.verify_id_token(token_schema.token)
        except InvalidIdTokenError:
            raise HTTPException(
                status_code=400,
                detail={"detail": "Invalid token", "code": "INVALID_TOKEN"}
            )
        except ExpiredIdTokenError:
            raise HTTPException(
                status_code=400,
                detail={"detail": "Token expired", "code": "TOKEN_EXPIRED"}
            )

        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")

        if not email:
            raise HTTPException(
                status_code=400,
                detail={"detail": "Email not found in token", "code": "EMAIL_MISSING"}
            )

        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.firebase_uid == firebase_uid) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.firebase_uid == firebase_uid:
                return existing_user

            raise HTTPException(
                status_code=400,
                detail={"detail": "Email already registered", "code": "EMAIL_EXISTS"}
            )
        
        # Create new user
        new_user = User(
            email=email,
            firebase_uid=firebase_uid,
            role=UserRole.STUDENT  # Default role
        )
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"New user registered: {email}")
            return new_user
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during user registration: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"detail": "Database error", "code": "DB_ERROR"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"detail": "Internal server error", "code": "INTERNAL_ERROR"}
        )

@router.get("/me", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
@limiter.limit("60/minute")
async def get_current_user(
    request: Request,
    token_schema: TokenSchema,
    db: Session = Depends(get_db)
):
    try:
        try:
            decoded_token = firebase_auth.verify_id_token(token_schema.token)
        except InvalidIdTokenError:
            raise HTTPException(
                status_code=400,
                detail={"detail": "Invalid token", "code": "INVALID_TOKEN"}
            )
        except ExpiredIdTokenError:
            raise HTTPException(
                status_code=400,
                detail={"detail": "Token expired", "code": "TOKEN_EXPIRED"}
            )

        user = db.query(User).filter(User.firebase_uid == decoded_token['uid']).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail={"detail": "User not found", "code": "USER_NOT_FOUND"}
            )
            
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"detail": "Internal server error", "code": "INTERNAL_ERROR"}
        )

@router.put("/update-role", response_model=UserResponse, responses={400: {"model": ErrorResponse}})
@limiter.limit("5/minute")
async def update_user_role(
    request: Request,
    token_schema: TokenSchema,
    new_role: UserRole,
    db: Session = Depends(get_db)
):
    try:
        decoded_token = firebase_auth.verify_id_token(token_schema.token)
        user = db.query(User).filter(User.firebase_uid == decoded_token['uid']).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail={"detail": "User not found", "code": "USER_NOT_FOUND"}
            )
            
        user.role = new_role
        
        try:
            db.commit()
            db.refresh(user)
            logger.info(f"Role updated for user {user.email}: {new_role}")
            return user
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during role update: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"detail": "Database error", "code": "DB_ERROR"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_user_role: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"detail": "Internal server error", "code": "INTERNAL_ERROR"}
        )
