import pytest
import uuid
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.models.models import Testimonial
from app.schemas.testimonial import TestimonialCreate, TestimonialUpdate
from app.services.testimonial_service import testimonial_service


def test_create_testimonial():
    """Test successfully creating a testimonial."""
    mock_db = MagicMock(spec=Session)
    testimonial_in = TestimonialCreate(
        name="John Doe",
        source="Google Reviews",
        comment="Great service and products!"
    )
    
    created_testimonial = testimonial_service.create(db=mock_db, obj_in=testimonial_in)
    
    assert created_testimonial.name == "John Doe"
    assert created_testimonial.source == "Google Reviews"
    assert created_testimonial.comment == "Great service and products!"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_get_active_for_website():
    """Test retrieving active testimonials ordered by sort_order."""
    mock_db = MagicMock(spec=Session)
    
    fake_t1 = Testimonial(name="User 1", is_active=True, sort_order=1)
    fake_t2 = Testimonial(name="User 2", is_active=True, sort_order=2)
    
    mock_execute = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [fake_t1, fake_t2]
    mock_execute.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_execute
    
    results = testimonial_service.get_active_for_website(db=mock_db, skip=0, limit=10)
    
    assert len(results) == 2
    assert results[0].name == "User 1"
    assert results[1].name == "User 2"
    mock_db.execute.assert_called_once()

def test_get_testimonial_found():
    """Test retrieving an existing testimonial by ID."""
    mock_db = MagicMock(spec=Session)
    test_id = uuid.uuid4()
    fake_testimonial = Testimonial(id=test_id, name="Found User", is_active=True)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = fake_testimonial
    mock_db.execute.return_value = mock_execute
    
    result = testimonial_service.get(db=mock_db, id=test_id)
    
    assert result is not None
    assert result.name == "Found User"
    mock_db.execute.assert_called_once()

def test_update_testimonial():
    """Test updating testimonial details."""
    mock_db = MagicMock(spec=Session)
    existing_testimonial = Testimonial(name="Old Name", comment="Old comment", is_active=True, sort_order=0)
    update_data = TestimonialUpdate(name="New Name", sort_order=10)
    
    updated_testimonial = testimonial_service.update(db=mock_db, db_obj=existing_testimonial, obj_in=update_data)
    
    assert updated_testimonial.name == "New Name"
    assert updated_testimonial.sort_order == 10
    assert updated_testimonial.comment == "Old comment"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_delete_testimonial_logical():
    """Test soft-deleting a testimonial."""
    mock_db = MagicMock(spec=Session)
    test_id = uuid.uuid4()
    existing_testimonial = Testimonial(id=test_id, name="To Delete", is_active=True)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = existing_testimonial
    mock_db.execute.return_value = mock_execute
    
    deleted_testimonial = testimonial_service.delete(db=mock_db, id=test_id)
    
    assert deleted_testimonial is not None
    assert deleted_testimonial.is_active is False
    mock_db.commit.assert_called_once()


def test_get_testimonial_not_found():
    """Test searching for a non-existent testimonial returns None."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute
    
    result = testimonial_service.get(db=mock_db, id=uuid.uuid4())
    
    assert result is None
    mock_db.execute.assert_called_once()

def test_delete_testimonial_not_found():
    """Test attempting to delete a non-existent testimonial returns None and does nothing."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute
    
    result = testimonial_service.delete(db=mock_db, id=uuid.uuid4())
    
    assert result is None
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

def test_get_active_for_website_empty():
    """Test retrieving active testimonials when none exist returns empty list."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_execute.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_execute
    
    results = testimonial_service.get_active_for_website(db=mock_db, skip=0, limit=10)
    
    assert results == []
    mock_db.execute.assert_called_once()
