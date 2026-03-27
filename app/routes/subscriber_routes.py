from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.db_connection import get_db
from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate, SubscriberOut, EmailDraft
from app.services.smtp.send_subscriber_service import send_batch_emails_smtp
from app.services.subscriber_service import subscriber_service
from app.core.security import get_current_active_user


router = APIRouter(prefix="/subscribers", tags=["Subscribers"])

# PAGE VISITORS ENDPOINTS

@router.post("/subscribe", response_model=SubscriberOut, status_code=status.HTTP_201_CREATED)
def subscribe_newsletter(
        subscriber_in: SubscriberCreate,
        db: Session = Depends(get_db)
):
    existing_sub = subscriber_service.get_by_email(db=db, email=subscriber_in.email)

    if existing_sub:
        if existing_sub.is_active:
            return existing_sub

        update_data = SubscriberUpdate(is_active=True)
        return subscriber_service.update(db=db, db_obj=existing_sub, obj_in=update_data)

    return subscriber_service.create(db=db, obj_in=subscriber_in)


@router.get("/unsubscribe/{id}")
def unsubscribe_newsletter(
        id: uuid.UUID,
        db: Session = Depends(get_db)
):
    sub = subscriber_service.get(db=db, id=id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscriber not found.")

    update_data = SubscriberUpdate(is_active=False)
    subscriber_service.update(db=db, db_obj=sub, obj_in=update_data)

    return {"message": "You have been successfully unsubscribed."}


# ENDPOINTS TO ADMINS

@router.get("/subscribers", response_model=List[SubscriberOut], dependencies=[Depends(get_current_active_user)])
def get_all_subscribers(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
):
    return subscriber_service.get_all_no_filtered(db=db, skip=skip, limit=limit)

@router.post("/send-email-batch", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(get_current_active_user)])
def send_newsletter_blast(
        blast_in: EmailDraft,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    try:
        all_subscribers = subscriber_service.get_multi(db=db, limit=10000)

        active_emails = [sub.email for sub in all_subscribers if sub.is_active]

        if not active_emails:
            raise HTTPException(status_code=400, detail="No active subscribers found.")

        background_tasks.add_task(
            send_batch_emails_smtp,
            subject=blast_in.subject,
            html_content=blast_in.html_content,
            destination_emails=active_emails
        )
        return {"message": f"Email blast queued for {len(active_emails)} subscribers."}
    except Exception as e:
        return {"message": str(e)}