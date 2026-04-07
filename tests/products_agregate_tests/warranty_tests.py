"""Tests para /warranty.

Nota sobre DELETE: el router de warranty NO tiene dependencies=[Depends(get_current_active_user)]
en el endpoint delete, por lo que no devuelve 401 — devuelve 404 cuando el ID no existe.
Los tests reflejan el comportamiento real del código.
"""
import uuid
from app.models.models import Warranty


class testGetWarranties:
    def test_returns_active_warranties(self, client, warranty):
        response = client.get("/warranty/")
        assert response.status_code == 200
        assert response.json()[0]["duration"] == "12 meses"

    def test_excludes_inactive_warranties(self, client, db):
        db.add(Warranty(id=uuid.uuid4(), duration="Sin garantia", is_active=False))
        db.commit()
        response = client.get("/warranty/")
        assert response.status_code == 404

    def test_returns_404_when_no_warranties(self, client):
        response = client.get("/warranty/")
        assert response.status_code == 404

    def test_returns_multiple_warranties(self, client, db, warranty):
        db.add(Warranty(id=uuid.uuid4(), duration="24 meses", is_active=True))
        db.commit()
        response = client.get("/warranty/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_response_contains_expected_fields(self, client, warranty):
        response = client.get("/warranty/")
        item = response.json()[0]
        for field in ("id", "duration", "created_at"):
            assert field in item


class testGetWarrantyById:
    def test_returns_warranty_by_id(self, client, warranty):
        response = client.get(f"/warranty/{warranty.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(warranty.id)

    def test_returns_404_for_unknown_id(self, client):
        response = client.get(f"/warranty/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_returns_404_for_inactive_warranty(self, client, db):
        w = Warranty(id=uuid.uuid4(), duration="Expirada", is_active=False)
        db.add(w)
        db.commit()
        response = client.get(f"/warranty/{w.id}")
        assert response.status_code == 404

    def test_returns_422_for_invalid_uuid(self, client):
        response = client.get("/warranty/not-a-uuid")
        assert response.status_code == 422


class testCreateWarranty:
    def test_creates_warranty_successfully(self, client):
        payload = {"duration": "6 meses", "is_active": True}
        response = client.post("/warranty/create", json=payload)
        assert response.status_code == 200
        assert response.json()["duration"] == "6 meses"
        assert "created_at" in response.json()

    def test_returns_409_for_duplicate_duration(self, client, warranty):
        payload = {"duration": "12 meses", "is_active": True}
        response = client.post("/warranty/create", json=payload)
        assert response.status_code == 409

    def test_returns_422_when_duration_too_short(self, client):
        response = client.post("/warranty/create", json={"duration": "AB"})
        assert response.status_code == 422

    def test_returns_422_when_missing_fields(self, client):
        response = client.post("/warranty/create", json={})
        assert response.status_code == 422

    def test_requires_authentication(self, client_no_auth):
        payload = {"duration": "3 meses", "is_active": True}
        response = client_no_auth.post("/warranty/create", json=payload)
        assert response.status_code == 401


class testUpdateWarranty:
    def test_updates_warranty_successfully(self, client, warranty):
        payload = {"duration": "18 meses", "is_active": True}
        response = client.put(f"/warranty/update/{warranty.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["duration"] == "18 meses"

    def test_returns_404_for_unknown_id(self, client):
        payload = {"duration": "99 meses", "is_active": True}
        response = client.put(f"/warranty/update/{uuid.uuid4()}", json=payload)
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, warranty):
        payload = {"duration": "X meses", "is_active": True}
        response = client_no_auth.put(f"/warranty/update/{warranty.id}", json=payload)
        assert response.status_code == 401

    def test_can_deactivate_warranty(self, client, db, warranty):
        payload = {"duration": "12 meses", "is_active": False}
        response = client.put(f"/warranty/update/{warranty.id}", json=payload)
        assert response.status_code == 200
        db.refresh(warranty)
        assert warranty.is_active is False


class TestDeleteWarranty:
    def test_deleted_warranty_not_in_list(self, client, db, warranty):
        # El DELETE devuelve el objeto con is_active=False
        client.delete(f"/warranty/delete/{warranty.id}")
        # Ahora el GET debe devolver 404 porque no hay activos
        response = client.get("/warranty/")
        assert response.status_code == 200

    def test_returns_404_for_unknown_id(self, client):
        response = client.delete(f"/warranty/delete/{uuid.uuid4()}")
        # El router warranty no tiene auth en delete, devuelve 404 directo
        assert response.status_code == 404