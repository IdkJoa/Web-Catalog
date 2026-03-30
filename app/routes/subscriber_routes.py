import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.db_connection import get_db
from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate, SubscriberOut, EmailDraft
from app.services.smtp.send_subscriber_service import send_batch_emails_smtp
from app.services.subscriber_service import subscriber_service
from app.core.security import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscribers", tags=["Subscribers"])

# PAGE VISITORS ENDPOINTS

@router.post("/subscribe", response_model=SubscriberOut, status_code=status.HTTP_201_CREATED)
def subscribe_newsletter(
        subscriber_in: SubscriberCreate,
        db: Session = Depends(get_db)
):
    logger.info(f"Subscription attempt for email: {subscriber_in.email}")
    existing_sub = subscriber_service.get_by_email(db=db, email=subscriber_in.email)

    if existing_sub:
        if existing_sub.is_active:
            logger.info(f"User {subscriber_in.email} is already subscribed and active")
            return existing_sub

        logger.info(f"Re-activating subscription for {subscriber_in.email}")
        update_data = SubscriberUpdate(is_active=True)
        return subscriber_service.update(db=db, db_obj=existing_sub, obj_in=update_data)

    new_sub = subscriber_service.create(db=db, obj_in=subscriber_in)
    logger.info(f"New subscription created for {subscriber_in.email} with id: {new_sub.id}")
    return new_sub


@router.get("/unsubscribe/{id}")
def unsubscribe_newsletter(
        id: uuid.UUID,
        db: Session = Depends(get_db)
):
    logger.info(f"Unsubscription request for id: {id}")
    sub = subscriber_service.get(db=db, id=id)
    if not sub:
        logger.warning(f"Unsubscribe failed: Subscriber {id} not found")
        raise HTTPException(status_code=404, detail="Subscriber not found.")

    update_data = SubscriberUpdate(is_active=False)
    subscriber_service.update(db=db, db_obj=sub, obj_in=update_data)
    logger.info(f"Subscriber {id} ({sub.email}) successfully unsubscribed")

    return {"message": "You have been successfully unsubscribed."}


# ENDPOINTS TO ADMINS

@router.get("/subscribers", response_model=List[SubscriberOut], dependencies=[Depends(get_current_active_user)])
def get_all_subscribers(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    logger.debug(f"Admin fetching all subscribers: skip={skip}, limit={limit}")
    return subscriber_service.get_all_no_filtered(db=db, skip=skip, limit=limit)

@router.get("/subscriber/{id}", response_model=SubscriberOut, dependencies=[Depends(get_current_active_user)])
def get_subscriber(
        id: uuid.UUID,
        db: Session = Depends(get_db)
):
    logger.debug(f"Admin fetching subscriber with id: {id}")
    sub = subscriber_service.get(db=db, id=id)
    if not sub:
        logger.warning(f"Admin fetch failed: Subscriber {id} not found")
        raise HTTPException(status_code=404, detail="Subscriber not found.")
    return sub

@router.post("/send-email-batch", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(get_current_active_user)])
def send_newsletter_blast(
        blast_in: EmailDraft,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    logger.info(f"Admin initiating email blast: {blast_in.subject}")
    try:
        all_subscribers = subscriber_service.get_multi(db=db, limit=10000)

        active_emails = [sub.email for sub in all_subscribers if sub.is_active]

        if not active_emails:
            logger.warning("Email blast failed: No active subscribers found")
            raise HTTPException(status_code=400, detail="No active subscribers found.")

        background_tasks.add_task(
            send_batch_emails_smtp,
            subject=blast_in.subject,
            html_content=blast_in.html_content,
            destination_emails=active_emails
        )
        logger.info(f"Email blast queued for {len(active_emails)} subscribers")
        return {"message": f"Email blast queued for {len(active_emails)} subscribers."}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error initiating email blast: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")