from unittest.mock import MagicMock
from sqlalchemy.orm import Session

# Adjust these imports to match your project paths!
from app.models.models import SiteSetting
from app.schemas.site_settings import SiteSettingsCreate, SiteSettingsUpdate
from app.services.site_settings_service import site_settings_service


# ==========================================
# 1. TEST: CREATE
# ==========================================
def test_site_settings_create():
    mock_db = MagicMock(spec=Session)

    # We must provide EVERY field that doesn't have a default value in your schema
    obj_in = SiteSettingsCreate(
        site_name="My Awesome Web Catalog",  # Assuming this is in your Base schema
        whatsapp="+1234567890",
        address="123 Catalog St, Web City",
        email="admin@catalog.com",
        meta_title="Web Catalog Home",
        meta_description="The best catalog on the web.",
        meta_keywords="catalog, web, items"
    )

    result = site_settings_service.create(db=mock_db, obj_in=obj_in)

    # Verify the mapping worked for a couple of your specific fields
    assert result.whatsapp == "+1234567890"
    assert result.email == "admin@catalog.com"

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


# ==========================================
# 2. TEST: GET (SINGLE)
# ==========================================
def test_site_settings_get():
    mock_db = MagicMock(spec=Session)

    fake_setting = SiteSetting(id=1, email="admin@catalog.com", is_active=True)
    mock_db.execute.return_value.scalar_one_or_none.return_value = fake_setting

    result = site_settings_service.get(db=mock_db, id=1)

    assert result is not None
    assert result.email == "admin@catalog.com"


# ==========================================
# 3. TEST: GET MULTI (ACTIVE ONLY)
# ==========================================
def test_site_settings_get_multi():
    mock_db = MagicMock(spec=Session)

    fake_list = [
        SiteSetting(id=1, email="siteA@test.com", is_active=True),
        SiteSetting(id=2, email="siteB@test.com", is_active=True)
    ]
    mock_db.execute.return_value.scalars.return_value.all.return_value = fake_list

    results = site_settings_service.get_multi(db=mock_db, skip=0, limit=10)

    assert len(results) == 2
    assert results[0].email == "siteA@test.com"


# ==========================================
# 4. TEST: GET ALL NO FILTERED
# ==========================================
def test_site_settings_get_all_no_filtered():
    mock_db = MagicMock(spec=Session)

    fake_list = [
        SiteSetting(id=1, is_active=True),
        SiteSetting(id=2, is_active=False)
    ]
    mock_db.execute.return_value.scalars.return_value.all.return_value = fake_list

    results = site_settings_service.get_all_no_filtered(db=mock_db)

    assert len(results) == 2
    assert results[0].is_active is True
    assert results[1].is_active is False


# ==========================================
# 5. TEST: UPDATE
# ==========================================
def test_site_settings_update():
    mock_db = MagicMock(spec=Session)

    db_obj = SiteSetting(id=1, email="old@test.com", whatsapp="000")

    # We only update the whatsapp number, the email should stay the same
    update_data = SiteSettingsUpdate(whatsapp="+999999999")

    result = site_settings_service.update(db=mock_db, db_obj=db_obj, obj_in=update_data)

    assert result.whatsapp == "+999999999"
    assert result.email == "old@test.com"  # Stays untouched

    mock_db.add.assert_called_with(db_obj)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_with(db_obj)


# ==========================================
# 6. TEST: SOFT DELETE
# ==========================================
def test_site_settings_delete():
    mock_db = MagicMock(spec=Session)

    db_obj = SiteSetting(id=1, is_active=True)
    mock_db.execute.return_value.scalar_one_or_none.return_value = db_obj

    result = site_settings_service.delete(db=mock_db, id=1)

    assert result.is_active is False

    mock_db.add.assert_called_with(db_obj)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_with(db_obj)