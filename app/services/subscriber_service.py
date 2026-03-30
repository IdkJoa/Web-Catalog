import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.base.crud_base import CRUDBase
from app.models.models import Subscriber
from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate

logger = logging.getLogger(__name__)

class CRUDSubscriber(CRUDBase[Subscriber, SubscriberCreate, SubscriberUpdate]):

    def get_by_email(self, db: Session, email: str):
        logger.debug(f"Fetching Subscriber with email: {email}")
        stmt = select(self.model).where(self.model.email == email)
        return db.execute(stmt).scalar_one_or_none()

subscriber_service = CRUDSubscriber(Subscriber)