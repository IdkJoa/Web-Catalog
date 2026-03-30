from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, logger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from typing import List
from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_active_user
from app.db.db_connection import get_db
from app.schemas.products import ProductCreate, ProductOut, ProductUpdate
from app.services.products_service import product_services

tracer = trace.get_tracer(__name__)

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "producto no encontrado"}},
)


@router.get("/", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_products") as span:
        try:
            products = product_services.get_multi(db)

            if products is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No hay productos activos",
                )

            span.set_attribute("http.status_code", 200)
            span.set_attribute("products.count", len(products))
            logger.info("Productos devueltos con éxito")
            return products

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_products: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_products: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.get("/offers", response_model=List[ProductOut])
def get_offers(db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_offers") as span:
        try:
            products = product_services.get_byoffer(db)

            span.set_attribute("http.status_code", 200)
            span.set_attribute("products.count", len(products))
            logger.info("Ofertas devueltas con éxito")
            return products

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_offers: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_offers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.get("/{id}", response_model=ProductOut)
def get_product(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_product_by_id") as span:
        try:
            span.set_attribute("product.id", str(id))
            product = product_services.get(db, id=id)

            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado",
                )

            span.set_attribute("http.status_code", 200)
            logger.info(f"Producto {id} devuelto con éxito")
            return product

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_product (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_product (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.get("/category/{category_id}", response_model=List[ProductOut])
def get_by_category(category_id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_by_category") as span:
        try:
            span.set_attribute("category.id", str(category_id))
            products = product_services.get_by_category(db, category_id)

            if not products:
                raise HTTPException(
                    status_code=404,
                    detail="No hay productos en esta categoria",
                )

            span.set_attribute("http.status_code", 200)
            span.set_attribute("products.count", len(products))
            logger.info(f"Productos de categoría {category_id} devueltos con éxito")
            return products

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_by_category (category_id={category_id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_by_category (category_id={category_id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.get("/brand/{brand_id}", response_model=List[ProductOut])
def get_by_brand(brand_id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("get_by_brand") as span:
        try:
            span.set_attribute("brand.id", str(brand_id))
            products = product_services.get_by_brand(db, brand_id)

            if not products:
                raise HTTPException(
                    status_code=404,
                    detail="No hay productos de esta marca",
                )

            span.set_attribute("http.status_code", 200)
            span.set_attribute("products.count", len(products))
            logger.info(f"Productos de marca {brand_id} devueltos con éxito")
            return products

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en get_by_brand (brand_id={brand_id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en get_by_brand (brand_id={brand_id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}",
            )


@router.post("/create", response_model=ProductOut, dependencies=[Depends(get_current_active_user)])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("create_product") as span:
        try:
            span.set_attribute("product.model_name", product.model_name)
            exist = product_services.get_byname(db, product.model_name)

            if exist:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Producto existente",
                )

            new_product = product_services.create(db=db, obj_in=product)

            span.set_attribute("http.status_code", 201)
            span.set_attribute("product.id", str(new_product.id))
            logger.info(f"Producto '{product.model_name}' creado con éxito (id={new_product.id})")
            return new_product

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en create_product (model={product.model_name}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en create_product (model={product.model_name}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}",
            )


@router.put("/update/{id}", response_model=ProductOut, dependencies=[Depends(get_current_active_user)])
def update_product(id: UUID, product: ProductUpdate, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("update_product") as span:
        try:
            span.set_attribute("product.id", str(id))
            exist = product_services.get(db, id)

            if exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado",
                )

            updated = product_services.update(db=db, obj_in=product, db_obj=exist)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Producto {id} actualizado con éxito")
            return updated

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en update_product (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en update_product (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}",
            )


@router.delete("/delete/{id}", response_model=ProductOut, dependencies=[Depends(get_current_active_user)])
def delete_product(id: UUID, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("delete_product") as span:
        try:
            span.set_attribute("product.id", str(id))
            exist = product_services.get(db, id)

            if exist is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado",
                )

            deleted = product_services.delete(db=db, id=id)

            span.set_attribute("http.status_code", 200)
            logger.info(f"Producto {id} eliminado con éxito")
            return deleted

        except HTTPException as http_exc:
            span.record_exception(http_exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(http_exc.detail)))
            logger.error(f"Error HTTP en delete_product (id={id}): {http_exc.detail}")
            raise http_exc
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error inesperado en delete_product (id={id}): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}",
            )