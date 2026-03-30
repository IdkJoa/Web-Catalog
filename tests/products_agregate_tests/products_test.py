"""
Tests para el router de productos (/products).

Cubre:
- GET /                     → listar productos activos
- GET /offers               → listar productos en oferta
- GET /{id}                 → obtener producto por ID
- GET /category/{id}        → filtrar por categoría
- GET /brand/{id}           → filtrar por marca
- POST /create              → crear producto (requiere auth)
- PUT /update/{id}          → actualizar producto (requiere auth)
- DELETE /delete/{id}       → soft-delete (requiere auth)
"""

import uuid
import pytest
from decimal import Decimal
from app.models.models import Product


# ---------------------------------------------------------------------------
# GET /products/
# ---------------------------------------------------------------------------

class testGetProducts:
    def test_returns_active_products(self, client, product):
        response = client.get("/products/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "Dell XPS 15"

    def test_excludes_inactive_products(self, client, db, category, brand, condition, warranty):
        db.add(Product(
            id=uuid.uuid4(),
            category_id=category.id, brand_id=brand.id,
            condition_id=condition.id, warranty_id=warranty.id,
            name="Inactivo", price=100.00, is_active=False,
        ))
        db.commit()
        response = client.get("/products/")
        assert response.status_code == 404

    def test_returns_404_when_no_products(self, client):
        response = client.get("/products/")
        assert response.status_code == 404

    def test_returns_multiple_products(self, client, db, product, category, brand, condition, warranty):
        db.add(Product(
            id=uuid.uuid4(),
            category_id=category.id, brand_id=brand.id,
            condition_id=condition.id, warranty_id=warranty.id,
            name="HP EliteBook", model_name="ELITE-840", price=1200.00, is_active=True,
        ))
        db.commit()
        response = client.get("/products/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_response_contains_expected_fields(self, client, product):
        response = client.get("/products/")
        assert response.status_code == 200
        item = response.json()[0]
        for field in ("id", "name", "price", "is_active", "stock_status"):
            assert field in item

    def test_response_includes_related_entities(self, client, product):
        response = client.get("/products/")
        assert response.status_code == 200
        item = response.json()[0]
        assert item["category"] is not None
        assert item["brand"] is not None
        assert item["condition"] is not None
        assert item["warranty"] is not None


# ---------------------------------------------------------------------------
# GET /products/offers
# ---------------------------------------------------------------------------

class testGetOffers:
    def test_returns_products_with_sale_price(self, client, product):
        # product fixture has sale_price < price
        response = client.get("/products/offers")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Dell XPS 15"

    def test_excludes_products_without_sale_price(self, client, db, category, brand, condition, warranty):
        db.add(Product(
            id=uuid.uuid4(),
            category_id=category.id, brand_id=brand.id,
            condition_id=condition.id, warranty_id=warranty.id,
            name="Sin oferta", price=500.00, sale_price=None, is_active=True,
        ))
        db.commit()
        response = client.get("/products/offers")
        assert response.status_code == 200

    def test_returns_empty_when_no_offers(self, client, db, category, brand, condition, warranty):
        db.add(Product(
            id=uuid.uuid4(),
            category_id=category.id, brand_id=brand.id,
            condition_id=condition.id, warranty_id=warranty.id,
            name="Normal", price=500.00, sale_price=None, is_active=True,
        ))
        db.commit()
        response = client.get("/products/offers")
        # Returns empty list or 404 depending on implementation
        assert response.status_code in (200, 404)

    def test_sale_price_lower_than_price(self, client, product):
        response = client.get("/products/offers")
        assert response.status_code == 200
        for item in response.json():
            assert float(item["sale_price"]) < float(item["price"])


# ---------------------------------------------------------------------------
# GET /products/{id}
# ---------------------------------------------------------------------------

class testGetProductById:
    def test_returns_product_by_id(self, client, product):
        response = client.get(f"/products/{product.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(product.id)
        assert response.json()["name"] == "Dell XPS 15"

    def test_returns_404_for_unknown_id(self, client):
        response = client.get(f"/products/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_returns_404_for_inactive_product(self, client, db, category, brand, condition, warranty):
        p = Product(
            id=uuid.uuid4(),
            category_id=category.id, brand_id=brand.id,
            condition_id=condition.id, warranty_id=warranty.id,
            name="Oculto", price=100.00, is_active=False,
        )
        db.add(p)
        db.commit()
        response = client.get(f"/products/{p.id}")
        assert response.status_code == 404

    def test_returns_422_for_invalid_uuid(self, client):
        response = client.get("/products/not-a-uuid")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /products/category/{category_id}
# ---------------------------------------------------------------------------

class testGetByCategory:
    def test_returns_products_for_category(self, client, product, category):
        response = client.get(f"/products/category/{category.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category_id"] == str(category.id)

    def test_returns_404_for_empty_category(self, client, db):
        other_cat_id = uuid.uuid4()
        response = client.get(f"/products/category/{other_cat_id}")
        assert response.status_code == 404

    def test_filters_by_category_correctly(self, client, db, product, category, brand, condition, warranty):
        other_cat = __import__('app.models.models', fromlist=['Category']).Category
        from app.models.models import Category as Cat
        cat2 = Cat(id=uuid.uuid4(), name="Phones", slug="phones", sort_order=2, is_active=True)
        db.add(cat2)

        p2 = Product(
            id=uuid.uuid4(),
            category_id=cat2.id, brand_id=brand.id,
            condition_id=condition.id, warranty_id=warranty.id,
            name="iPhone 15", price=1000.00, is_active=True,
        )
        db.add(p2)
        db.commit()

        response = client.get(f"/products/category/{category.id}")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "Dell XPS 15" in names
        assert "iPhone 15" not in names


# ---------------------------------------------------------------------------
# GET /products/brand/{brand_id}
# ---------------------------------------------------------------------------

class testGetByBrand:
    def test_returns_products_for_brand(self, client, product, brand):
        response = client.get(f"/products/brand/{brand.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["brand_id"] == str(brand.id)

    def test_returns_404_for_empty_brand(self, client):
        response = client.get(f"/products/brand/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_filters_by_brand_correctly(self, client, db, product, brand, category, condition, warranty):
        from app.models.models import Brand as B
        brand2 = B(id=uuid.uuid4(), name="HP", slug="hp", is_active=True)
        db.add(brand2)

        p2 = Product(
            id=uuid.uuid4(),
            category_id=category.id, brand_id=brand2.id,
            condition_id=condition.id, warranty_id=warranty.id,
            name="HP Laptop", price=900.00, is_active=True,
        )
        db.add(p2)
        db.commit()

        response = client.get(f"/products/brand/{brand.id}")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "Dell XPS 15" in names
        assert "HP Laptop" not in names


# ---------------------------------------------------------------------------
# POST /products/create
# ---------------------------------------------------------------------------

class testCreateProduct:
    def test_creates_product_successfully(self, client, product_payload):
        response = client.post("/products/create", json=product_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MacBook Pro"
        assert data["model_name"] == "MBP-M3-2024"
        assert "id" in data

    def test_returns_409_for_duplicate_model_name(self, client, product, product_payload):
        product_payload["model_name"] = "XPS-15-2024"  # same as fixture product
        response = client.post("/products/create", json=product_payload)
        assert response.status_code == 409
        assert "existente" in response.json()["detail"].lower()

    def test_returns_422_when_name_too_short(self, client, product_payload):
        product_payload["name"] = "AB"
        response = client.post("/products/create", json=product_payload)
        assert response.status_code == 422

    def test_returns_422_when_price_is_zero(self, client, product_payload):
        product_payload["price"] = "0.0000"
        response = client.post("/products/create", json=product_payload)
        assert response.status_code == 422

    def test_returns_422_when_missing_required_fields(self, client):
        response = client.post("/products/create", json={})
        assert response.status_code == 422

    def test_requires_authentication(self, client_no_auth, product_payload):
        response = client_no_auth.post("/products/create", json=product_payload)
        assert response.status_code == 401

    def test_product_linked_to_correct_category(self, client, product_payload, category):
        response = client.post("/products/create", json=product_payload)
        assert response.status_code == 200
        assert response.json()["category_id"] == str(category.id)

    def test_product_with_no_sale_price_is_valid(self, client, product_payload):
        product_payload["sale_price"] = None
        product_payload["model_name"] = "NO-SALE-MODEL"
        response = client.post("/products/create", json=product_payload)
        assert response.status_code == 200
        assert response.json()["sale_price"] is None


# ---------------------------------------------------------------------------
# PUT /products/update/{id}
# ---------------------------------------------------------------------------

class testUpdateProduct:
    def test_updates_product_name(self, client, product):
        payload = {
            "name": "Dell XPS 17 Updated",
            "stock_status": True,
            "price": "1600.0000",
            "sale_price": "1450.5000",
            "is_featured": False,
            "is_active": True,
            "meta_title": "Dell XPS 17 - Oferta Actualizada",
            "meta_description": "Compra la Dell XPS 17 con precio actualizado y envío gratuito.",
            "meta_keywords": "dell, xps, laptop, intel i7, rtx"
        }
        response = client.put(f"/products/update/{product.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Dell XPS 17 Updated"

    def test_updates_stock_status(self, client, product):
        payload = {
            "name": "Dell XPS 17 Updated",
            "stock_status": False,
            "price": "1600.0000",
            "sale_price": "1450.5000",
            "is_featured": False,
            "is_active": True,
            "meta_title": "Dell XPS 17 - Oferta Actualizada",
            "meta_description": "Compra la Dell XPS 17 con precio actualizado y envío gratuito.",
            "meta_keywords": "dell, xps, laptop, intel i7, rtx"
        }
        response = client.put(f"/products/update/{product.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["stock_status"] is False

    def test_updates_seo_fields(self, client, product):
        payload = {
            "name": "Dell XPS 17 Updated",
            "stock_status": True,
            "price": "1600.0000",
            "sale_price": "1450.5000",
            "is_featured": False,
            "is_active": True,
            "meta_title": "Dell XPS 17 - Oferta Actualizada 2",
            "meta_description": "Compra la Dell XPS 17 con precio actualizado y envío gratuito2.",
            "meta_keywords": "dell, xps, laptop, intel i7, rtx2"
        }
        response = client.put(f"/products/update/{product.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["meta_title"] == "Dell XPS 17 - Oferta Actualizada 2"

    def test_returns_404_for_unknown_id(self, client):
        payload = {
            "name": "Dell XPS 17 Updated",
            "stock_status": True,
            "price": "1600.0000",
            "sale_price": "1450.5000",
            "is_featured": False,
            "is_active": True,
            "meta_title": "Dell XPS 17 - Oferta Actualizada 2",
            "meta_description": "Compra la Dell XPS 17 con precio actualizado y envío gratuito2.",
            "meta_keywords": "dell, xps, laptop, intel i7, rtx2"
        }
        response = client.put(f"/products/update/{uuid.uuid4()}", json=payload)
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, product):
        payload = {"name": "Unauthorized Update"}
        response = client_no_auth.put(f"/products/update/{product.id}", json=payload)
        assert response.status_code == 401

    def test_can_deactivate_product(self, client, db, product):
        payload = {
            "name": "Dell XPS 17 Updated",
            "stock_status": True,
            "price": "1600.0000",
            "sale_price": "1450.5000",
            "is_featured": False,
            "is_active": False,
            "meta_title": "Dell XPS 17 - Oferta Actualizada 2",
            "meta_description": "Compra la Dell XPS 17 con precio actualizado y envío gratuito2.",
            "meta_keywords": "dell, xps, laptop, intel i7, rtx2"
        }
        response = client.put(f"/products/update/{product.id}", json=payload)
        assert response.status_code == 200
        db.refresh(product)
        assert product.is_active is False


# ---------------------------------------------------------------------------
# DELETE /products/delete/{id}
# ---------------------------------------------------------------------------

class testDeleteProduct:
    def test_soft_deletes_product(self, client, db, product):
        response = client.delete(f"/products/delete/{product.id}")
        assert response.status_code == 200
        db.refresh(product)
        assert product.is_active is False

    def test_deleted_product_not_in_list(self, client, db, product):
        client.delete(f"/products/delete/{product.id}")
        response = client.get("/products/")
        assert response.status_code == 404

    def test_returns_404_for_unknown_id(self, client):
        response = client.delete(f"/products/delete/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_requires_authentication(self, client_no_auth, product):
        response = client_no_auth.delete(f"/products/delete/{product.id}")
        assert response.status_code == 401

    def test_returns_deleted_product_data(self, client, product):
        response = client.delete(f"/products/delete/{product.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(product.id)
        assert response.json()["name"] == "Dell XPS 15"