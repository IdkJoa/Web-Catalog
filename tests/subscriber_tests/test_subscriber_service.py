import pytest
import uuid
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.models.models import Subscriber
from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate
from app.services.subscriber_service import subscriber_service

# ==========================================
# HAPPY PATHS
# ==========================================

def test_create_subscriber():
    """Test successfully creating a subscriber."""
    mock_db = MagicMock(spec=Session)
    subscriber_in = SubscriberCreate(email="test@example.com")
    
    # CRUDBase.create uses jsonable_encoder and then instantiates the model
    created_subscriber = subscriber_service.create(db=mock_db, obj_in=subscriber_in)
    
    assert created_subscriber.email == "test@example.com"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_get_subscriber_by_email_found():
    """Test retrieving an existing subscriber by email."""
    mock_db = MagicMock(spec=Session)
    fake_subscriber = Subscriber(email="exists@example.com", id=uuid.uuid4())
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = fake_subscriber
    mock_db.execute.return_value = mock_execute
    
    result = subscriber_service.get_by_email(db=mock_db, email="exists@example.com")
    
    assert result is not None
    assert result.email == "exists@example.com"
    mock_db.execute.assert_called_once()

def test_get_subscriber_by_id_found():
    """Test retrieving an existing subscriber by ID (inherited from CRUDBase)."""
    mock_db = MagicMock(spec=Session)
    sub_id = uuid.uuid4()
    fake_subscriber = Subscriber(email="id@example.com", id=sub_id, is_active=True)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = fake_subscriber
    mock_db.execute.return_value = mock_execute
    
    result = subscriber_service.get(db=mock_db, id=sub_id)
    
    assert result is not None
    assert result.id == sub_id
    mock_db.execute.assert_called_once()

def test_update_subscriber_status():
    """Test updating subscriber's active status."""
    mock_db = MagicMock(spec=Session)
    existing_sub = Subscriber(email="update@example.com", is_active=True)
    update_data = SubscriberUpdate(is_active=False)
    
    updated_sub = subscriber_service.update(db=mock_db, db_obj=existing_sub, obj_in=update_data)
    
    assert updated_sub.is_active is False
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_delete_subscriber_logical():
    """Test soft-deleting a subscriber."""
    mock_db = MagicMock(spec=Session)
    sub_id = uuid.uuid4()
    existing_sub = Subscriber(id=sub_id, email="delete@example.com", is_active=True)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = existing_sub
    mock_db.execute.return_value = mock_execute
    
    deleted_sub = subscriber_service.delete(db=mock_db, id=sub_id)
    
    assert deleted_sub is not None
    assert deleted_sub.is_active is False
    mock_db.commit.assert_called_once()

# ==========================================
# SAD PATHS / EDGE CASES
# ==========================================

def test_get_subscriber_by_email_not_found():
    """Test searching for a non-existent email returns None."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute
    
    result = subscriber_service.get_by_email(db=mock_db, email="ghost@example.com")
    
    assert result is None
    mock_db.execute.assert_called_once()

def test_get_subscriber_by_id_not_found():
    """Test searching for a non-existent ID returns None."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute
    
    result = subscriber_service.get(db=mock_db, id=uuid.uuid4())
    
    assert result is None

def test_delete_subscriber_not_found():
    """Test attempting to delete a non-existent subscriber returns None and does nothing."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute
    
    result = subscriber_service.delete(db=mock_db, id=uuid.uuid4())
    
    assert result is None
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
