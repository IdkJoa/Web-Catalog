"""Tests para /category"""
import uuid
from app.models.models import Category


class testGetCategories:
    def test_returns_active_categories(self, client, category):
        response = client.get("/category/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Laptops"

    def test_returns_404_when_no_categories(self, client):
        response = client.get("/category/")
        assert response.status_code == 404

    def test_returns_multiple_categories(self, client, db, category):
        db.add(Category(id=uuid.uuid4(), name="Monitores", slug="monitores", sort_order=2, is_active=True))
        db.commit()
        response = client.get("/category/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_response_contains_expected_fields(self, client, category):
        response = client.get("/category/")
        item = response.json()[0]
        for field in ("id", "name", "slug", "is_active"):
            assert field in item


class testGetCategoryById:
    def test_returns_category_by_id(self, client, category):
        response = client.get(f"/category/{category.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(category.id)

    def test_returns_404_for_unknown_id(self, client):
        response = client.get(f"/category/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_returns_404_for_inactive_category(self, client, db):
        cat = Category(id=uuid.uuid4(), name="Antigua", slug="antigua", sort_order=1, is_active=False)
        db.add(cat)
        db.commit()
        response = client.get(f"/category/{cat.id}")
        assert response.status_code == 404

    def test_returns_422_for_invalid_uuid(self, client):
        response = client.get("/category/not-a-uuid")
        assert response.status_code == 422


class testCreateCategory:
    def test_creates_category_successfully(self, client):
        payload = {
            "name": "Tablets de Alta Gama",
            "slug": "tablets-alta-gama",
            "description": "Explora nuestra selección de tablets de última generación para productividad y entretenimiento.",
            "image_url": "http://example.com/images/tablets.jpg",
            "sort_order": 1,
            "is_active": True,
            "meta_title": "Comprar Tablets Online | Web'Catalog",
            "meta_description": "Encuentra las mejores ofertas en tablets con garantía y envío rápido.",
            "meta_keywords": "tablets, tecnología, gadgets, ipad, android tablets"
        }
        response = client.post("/category/create", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Tablets de Alta Gama"

    def test_returns_409_for_duplicate_name(self, client, category):
        # mismo name que el fixture "Laptops"
        payload = {
            "name": "Laptops",
            "slug": "laptops",
            "description": "Categoría de laptops de alta gama y oficina",
            "image_url": "http://example.com/images/laptops.png",
            "sort_order": 1,
            "is_active": True,
            "meta_title": "Laptops y Computadoras Portátiles",
            "meta_description": "Compra las mejores laptops con garantía extendida.",
            "meta_keywords": "laptops, portatiles, gaming, oficina"
        }
        response = client.post("/category/create", json=payload)
        assert response.status_code == 409

    def test_returns_422_when_name_too_short(self, client):
        response = client.post("/category/create", json={"name": "AB", "slug": "ab", "sort_order": 1})
        assert response.status_code == 422

    def test_returns_422_when_missing_required_fields(self, client):
        response = client.post("/category/create", json={})
        assert response.status_code == 422

    def test_requires_authentication(self, client_no_auth):
        payload = {"name": "Test", "slug": "products_agregate_tests", "sort_order": 1, "is_active": True}
        response = client_no_auth.post("/category/create", json=payload)
        assert response.status_code == 401


class testUpdateCategory:
    def test_updates_category_successfully(self, client, category):
        # slug es requerido en CategoryBase
        payload = {
            "name": "Laptops act",
            "slug": "laptops",
            "description": "Categoría de laptops de alta gama y oficina",
            "image_url": "http://example.com/images/laptops.png",
            "sort_order": 1,
            "is_active": True,
            "meta_title": "Laptops y Computadoras Portátiles",
            "meta_description": "Compra las mejores laptops con garantía extendida.",
            "meta_keywords": "laptops, portatiles, gaming, oficina"
        }
        response = client.put(f"/category/update/{category.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Laptops act"

    def test_returns_404_for_unknown_id(self, client):
        payload = {
            "name": "Laptops act",
            "slug": "laptops",
            "description": "Categoría de laptops de alta gama y oficina",
            "image_url": "http://example.com/images/laptops.png",
            "sort_order": 1,
            "is_active": True,
            "meta_title": "Laptops y Computadoras Portátiles",
            "meta_description": "Compra las mejores laptops con garantía extendida.",
            "meta_keywords": "laptops, portatiles, gaming, oficina"
        }
        response = client.put(f"/category/update/{uuid.uuid4()}", json=payload)
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, category):
        payload = {"name": "Y cat", "slug": "y-cat", "sort_order": 1, "is_active": True}
        response = client_no_auth.put(f"/category/update/{category.id}", json=payload)
        assert response.status_code == 401


class testDeleteCategory:
    def test_soft_deletes_category(self, client, db, category):
        response = client.delete(f"/category/delete/{category.id}")
        assert response.status_code == 200
        db.refresh(category)
        assert category.is_active is False

    def test_returns_404_for_unknown_id(self, client):
        response = client.delete(f"/category/delete/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, category):
        response = client_no_auth.delete(f"/category/delete/{category.id}")
        assert response.status_code == 401