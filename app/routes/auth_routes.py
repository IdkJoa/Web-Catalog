import logging
from fastapi import  HTTPException, APIRouter, BackgroundTasks, security
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
from sqlalchemy.orm import Session
from app.core import security
from app.db.db_connection import get_db
from app.schemas import schemas
from app.schemas.schemas import PasswordRecovery, PasswordReset
from app.services.auth import register_user
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.AdminUserOut, status_code=status.HTTP_201_CREATED)
def register(
    user_in: schemas.AdminUserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
        email_service: EmailService = Depends()
):
    logger.info(f"Registration attempt for email: {user_in.email}")
    existing_user = register_user.admin.get_by_email(db, email=user_in.email)
    if existing_user:
        logger.warning(f"Registration failed: Email {user_in.email} already registered")
        raise HTTPException(status_code=400, detail="Email already registered")

    user = register_user.admin.create(db=db, obj_in=user_in)

    token = security.create_email_token(user.email)
    background_tasks.add_task(email_service.send_verification_email, user.email, token)
    logger.info(f"Successfully registered user: {user.email}. Verification email queued.")

    return user

@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    logger.info(f"Login attempt for user: {form_data.username}")
    user = register_user.admin.get_by_email(db, email=form_data.username)

    if not user:
        logger.warning(f"Login failed: User {form_data.username} not found")
        security.verify_dummy()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not security.verify_password(form_data.password, user.password):
        logger.warning(f"Login failed: Incorrect password for user {form_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_confirmed:
        logger.warning(f"Login failed: Account not verified for user {form_data.username}")
        raise HTTPException(status_code=403, detail="Please verify your email ")

    access_token = security.create_access_token(subject=str(user.id))
    logger.info(f"Successful login for user: {form_data.username}")

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    logger.info("Email verification attempt")
    email = security.decode_token(token, expected_type="email_confirm")

    if not email:
        logger.warning("Email verification failed: Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token."
        )

    user = register_user.admin.get_by_email(db, email=email)

    if not user:
        logger.warning(f"Email verification failed: User with email {email} not found")
        raise HTTPException(status_code=404, detail="User not found.")

    if user.is_confirmed:
        logger.info(f"Email verification: User {email} already verified")
        return {"message": "Account is already verified. You can log in."}

    register_user.admin.confirm_user(db, db_obj=user)
    logger.info(f"Email successfully verified for user: {email}")

    return {"message": "Email successfully verified! You may now log in."}

@router.post("/forgot-password")
def recover_password(
    recovery_in: PasswordRecovery,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends()
):
    logger.info(f"Password recovery requested for email: {recovery_in.email}")
    user = register_user.admin.get_by_email(db, email=recovery_in.email)

    if user and user.is_active:
        reset_token = security.create_password_reset_token(user.email)
        background_tasks.add_task(email_service.send_reset_email, user.email, reset_token)
        logger.info(f"Password reset email queued for user: {recovery_in.email}")
    else:
        logger.info(f"Password recovery: User {recovery_in.email} not found or inactive. No email sent.")

    return {"message": "If an account with that email exists, a password reset email will be sent. The password link will be sent"}


@router.patch("/reset-password")
def reset_password(body: PasswordReset, db: Session = Depends(get_db)):
    logger.info("Password reset attempt")
    email = security.decode_token(body.token, expected_type="password_reset")
    if not email:
        logger.warning("Password reset failed: Invalid or expired token")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    user = register_user.admin.get_by_email(db, email=email)
    if not user or not user.is_active:
        logger.warning(f"Password reset failed: User {email} not found or inactive")
        raise HTTPException(status_code=404, detail="User not found or inactive.")

    user.password = security.hash_password(body.new_password)
    db.commit()
    logger.info(f"Password updated successfully for user: {email}")

    return {"message": "Password updated successfully. You may now log in."}
