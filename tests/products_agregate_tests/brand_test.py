"""Tests para /brand"""
import uuid
from app.models.models import Brand


class testGetBrands:
    def test_returns_active_brands(self, client, brand):
        response = client.get("/brand/")
        assert response.status_code == 200
        assert response.json()[0]["name"] == "Dell"

    def test_excludes_inactive_brands(self, client, db):
        db.add(Brand(id=uuid.uuid4(), name="Inactiva", slug="inactiva", is_active=False))
        db.commit()
        response = client.get("/brand/")
        assert response.status_code == 404

    def test_returns_404_when_no_brands(self, client):
        response = client.get("/brand/")
        assert response.status_code == 404


    def test_response_contains_expected_fields(self, client, brand):
        response = client.get("/brand/")
        item = response.json()[0]
        for field in ("id", "name", "slug", "is_active"):
            assert field in item


class testGetBrandById:
    def test_returns_brand_by_id(self, client, brand):
        response = client.get(f"/brand/{brand.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(brand.id)

    def test_returns_404_for_unknown_id(self, client):
        response = client.get(f"/brand/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_returns_404_for_inactive_brand(self, client, db):
        b = Brand(id=uuid.uuid4(), name="Antigua", slug="antigua", is_active=False)
        db.add(b)
        db.commit()
        response = client.get(f"/brand/{b.id}")
        assert response.status_code == 404

    def test_returns_422_for_invalid_uuid(self, client):
        response = client.get("/brand/not-a-uuid")
        assert response.status_code == 422


class testCreateBrand:
    def test_creates_brand_successfully(self, client):
        payload = {"name": "Lenovo", "slug": "lenovo", "is_active": True}
        response = client.post("/brand/create", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Lenovo"

    def test_returns_409_for_duplicate_name(self, client, brand):
        payload = {"name": "Dell", "slug": "dell-2", "is_active": True}
        response = client.post("/brand/create", json=payload)
        assert response.status_code == 409

    def test_returns_422_when_name_too_short(self, client):
        response = client.post("/brand/create", json={"name": "AB", "slug": "ab"})
        assert response.status_code == 422

    def test_returns_422_when_missing_fields(self, client):
        response = client.post("/brand/create", json={})
        assert response.status_code == 422

    def test_requires_authentication(self, client_no_auth):
        payload = {"name": "Sony", "slug": "sony", "is_active": True}
        response = client_no_auth.post("/brand/create", json=payload)
        assert response.status_code == 401


class testUpdateBrand:
    def test_updates_brand_successfully(self, client, brand):
        payload = {"name": "Dell Technologies", "slug": "dell-technologies", "is_active": True}
        response = client.put(f"/brand/update/{brand.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Dell Technologies"

    def test_returns_404_for_unknown_id(self, client):
        payload = {"name": "X brand", "slug": "x-brand", "is_active": True}
        response = client.put(f"/brand/update/{uuid.uuid4()}", json=payload)
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, brand):
        payload = {"name": "Y brand", "slug": "y-brand", "is_active": True}
        response = client_no_auth.put(f"/brand/update/{brand.id}", json=payload)
        assert response.status_code == 401


class testDeleteBrand:
    def test_soft_deletes_brand(self, client, db, brand):
        response = client.delete(f"/brand/delete/{brand.id}")
        assert response.status_code == 200
        db.refresh(brand)
        assert brand.is_active is False

    def test_returns_404_for_unknown_id(self, client):
        response = client.delete(f"/brand/delete/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, brand):
        response = client_no_auth.delete(f"/brand/delete/{brand.id}")
        assert response.status_code == 401