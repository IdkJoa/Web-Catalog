import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from pydantic import ValidationError

# Adjust these imports to match your project paths!
from app.models.models import SocialNetwork
from app.schemas.social_network import SocialNetworkCreate, SocialNetworkUpdate
from app.services.social_network_service import social_network_service


def test_social_network_create_success():
    """Test creating a valid social network link."""
    mock_db = MagicMock(spec=Session)

    obj_in = SocialNetworkCreate(
        name="Instagram",
        url="https://instagram.com/mycatalog"
    )

    result = social_network_service.create(db=mock_db, obj_in=obj_in)

    assert result.name == "Instagram"
    assert result.url == "https://instagram.com/mycatalog"

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_social_network_get_success():
    """Test retrieving an existing social network."""
    mock_db = MagicMock(spec=Session)

    fake_network = SocialNetwork(id=1, name="Twitter", is_active=True)
    mock_db.execute.return_value.scalar_one_or_none.return_value = fake_network

    result = social_network_service.get(db=mock_db, id=1)

    assert result is not None
    assert result.name == "Twitter"


def test_social_network_get_multi():
    """Test retrieving a list of active social networks."""
    mock_db = MagicMock(spec=Session)

    fake_list = [
        SocialNetwork(id=1, name="Facebook", is_active=True),
        SocialNetwork(id=2, name="TikTok", is_active=True)
    ]
    mock_db.execute.return_value.scalars.return_value.all.return_value = fake_list

    results = social_network_service.get_multi(db=mock_db, skip=0, limit=10)

    assert len(results) == 2
    assert results[0].name == "Facebook"
    assert results[1].name == "TikTok"


def test_social_network_update_success():
    """Test updating an existing social network."""
    mock_db = MagicMock(spec=Session)
    db_obj = SocialNetwork(id=1, name="Facebook", url="https://old-link.com")

    update_data = SocialNetworkUpdate(
        name="Facebook",
        url="https://new-link.com",
        is_active=True
    )

    result = social_network_service.update(db=mock_db, db_obj=db_obj, obj_in=update_data)

    assert result.name == "Facebook"
    assert str(result.url) == "https://new-link.com/"

    mock_db.commit.assert_called_once()


def test_social_network_delete_success():
    """Test soft-deleting an existing social network."""
    mock_db = MagicMock(spec=Session)

    db_obj = SocialNetwork(id=1, name="DeleteMe", is_active=True)
    mock_db.execute.return_value.scalar_one_or_none.return_value = db_obj

    result = social_network_service.delete(db=mock_db, id=1)

    assert result.is_active is False
    mock_db.commit.assert_called_once()


# NEGATIVE TESTS

def test_social_network_create_missing_fields():
    """Test that Pydantic rejects creation if required fields are missing."""
    # We expect this to throw a ValidationError because we are omitting 'url'
    with pytest.raises(ValidationError):
        SocialNetworkCreate(name="Incomplete Network")


def test_social_network_create_invalid_url_format():
    """Test that Pydantic rejects badly formatted URLs (if strictly typed)."""
    with pytest.raises(ValidationError):
        SocialNetworkCreate(name="Bad URL", url="not-a-real-website")


def test_social_network_get_not_found():
    """Test requesting an ID that does not exist in the database."""
    mock_db = MagicMock(spec=Session)
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    result = social_network_service.get(db=mock_db, id=999)

    assert result is None


def test_social_network_delete_not_found():
    """Test attempting to delete an ID that does not exist."""
    mock_db = MagicMock(spec=Session)
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    result = social_network_service.delete(db=mock_db, id=999)

    assert result is None

    mock_db.commit.assert_not_called()