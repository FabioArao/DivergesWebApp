import firebase_admin
from firebase_admin import credentials, auth
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

def init_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
            })
            
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise

def verify_firebase_token(id_token: str) -> dict:
    """Verify Firebase ID token and return decoded token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.error(f"Failed to verify Firebase token: {str(e)}")
        raise

def get_user_by_uid(uid: str):
    """Get Firebase user by UID"""
    try:
        return auth.get_user(uid)
    except auth.UserNotFoundError:
        logger.error(f"User not found: {uid}")
        raise
    except Exception as e:
        logger.error(f"Failed to get user {uid}: {str(e)}")
        raise

def create_custom_token(uid: str, claims: dict = None):
    """Create a custom token for a user"""
    try:
        return auth.create_custom_token(uid, claims)
    except Exception as e:
        logger.error(f"Failed to create custom token for {uid}: {str(e)}")
        raise
