import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.models.models import Banner
from app.schemas.banner import BannerCreate, BannerUpdate
from app.services.banner_service import banner

def test_get_active_for_website():
    """Test retrieving active banners ordered by sort_order."""
    mock_db = MagicMock(spec=Session)
    
    fake_banner_1 = Banner(title="Promo 1", is_active=True, sort_order=1)
    fake_banner_2 = Banner(title="Promo 2", is_active=True, sort_order=2)
    
    # Mocking db.execute(stmt).scalars().all()
    mock_execute = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [fake_banner_1, fake_banner_2]
    mock_execute.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_execute
    
    results = banner.get_active_for_website(db=mock_db, skip=0, limit=10)
    
    assert len(results) == 2
    assert results[0].title == "Promo 1"
    assert results[1].title == "Promo 2"
    mock_db.execute.assert_called_once()

def test_create_banner():
    """Test creating a new banner."""
    mock_db = MagicMock(spec=Session)
    
    banner_in = BannerCreate(
        title="Summer Sale",
        image_url="http://example.com/summer.png",
        link="http://example.com/sale",
        sort_order=1,
        is_active=True
    )
    
    created_banner = banner.create(db=mock_db, obj_in=banner_in)
    
    assert created_banner.title == "Summer Sale"
    assert created_banner.image_url == "http://example.com/summer.png"
    assert created_banner.link == "http://example.com/sale"
    assert created_banner.sort_order == 1
    assert created_banner.is_active is True
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_get_banner():
    """Test retrieving a single banner by ID."""
    mock_db = MagicMock(spec=Session)
    
    fake_banner = Banner(title="Existing Promo", is_active=True)
    
    # Mocking db.execute(stmt).scalar_one_or_none()
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = fake_banner
    mock_db.execute.return_value = mock_execute
    
    result = banner.get(db=mock_db, id="123")
    
    assert result is not None
    assert result.title == "Existing Promo"
    mock_db.execute.assert_called_once()

def test_update_banner():
    """Test updating an existing banner."""
    mock_db = MagicMock(spec=Session)
    
    existing_banner = Banner(title="Old Promo", is_active=True, image_url="old.png", sort_order=1)
    update_data = BannerUpdate(title="New Promo", sort_order=5)
    
    updated_banner = banner.update(db=mock_db, db_obj=existing_banner, obj_in=update_data)
    
    assert updated_banner.title == "New Promo"
    assert updated_banner.sort_order == 5
    assert updated_banner.image_url == "old.png" # Ensure untouched fields remain untouched
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_delete_banner():
    """Test logical deletion of a banner."""
    mock_db = MagicMock(spec=Session)
    
    existing_banner = Banner(title="To Delete", is_active=True)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = existing_banner
    mock_db.execute.return_value = mock_execute
    
    deleted_banner = banner.delete(db=mock_db, id="123")
    
    assert deleted_banner is not None
    assert deleted_banner.is_active is False
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_get_banner_not_found():
    """Test retrieving a non-existent banner returns None."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute
    
    result = banner.get(db=mock_db, id="999")
    
    assert result is None
    mock_db.execute.assert_called_once()

def test_delete_banner_not_found():
    """Test attempting to delete a non-existent banner returns None and doesn't commit."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_execute.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_execute
    
    deleted_banner = banner.delete(db=mock_db, id="999")
    
    assert deleted_banner is None
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

def test_get_active_for_website_empty():
    """Test retrieving active banners when none exist returns empty list."""
    mock_db = MagicMock(spec=Session)
    
    mock_execute = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_execute.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_execute
    
    results = banner.get_active_for_website(db=mock_db, skip=0, limit=10)
    
    assert results == []
    mock_db.execute.assert_called_once()