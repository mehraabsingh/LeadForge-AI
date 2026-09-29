"""
Auth service - handles registration and login business logic.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, LoginRequest, Token, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
import logging

logger = logging.getLogger(__name__)


class AuthService:
    def register(self, db: Session, user_in: UserCreate) -> Token:
        # Check if email already exists
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        user = User(
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            role=user_in.role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user registered: {user.email} ({user.role})")

        token = create_access_token({"sub": user.id})
        return Token(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    def login(self, db: Session, login_data: LoginRequest) -> Token:
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled. Contact your administrator.",
            )
        logger.info(f"User logged in: {user.email}")
        token = create_access_token({"sub": user.id})
        return Token(
            access_token=token,
            user=UserResponse.model_validate(user),
        )


auth_service = AuthService()
