from fastapi.middleware.cors import CORSMiddleware
from app.routes import banner_routes, site_settings_routes, subscriber_routes, banner_upload_routes
from app.routes.products_routes import router as routes_products
from app.routes.category_routes import router as routes_category
from app.routes.warranty_routes import router as routes_warranty
from app.routes.brand_routes import router as routes_brand
from app.routes.condition_routes import router as routes_condition
from app.routes.capacity_routes import router as routes_capacity
from app.routes import auth_routes, testimonial_routes, social_network_routes
from telemetry import setup_telemetry
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Busca esta línea en tu archivo principal (main.py o donde inicialices el tracing)
setup_telemetry("webcatalogo-service")
app = FastAPI(
    title="Web'Catalog API",
    description="Backend API for managing products and content",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    'http://localhost:4200'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(testimonial_routes.router)
app.include_router(banner_routes.router)
app.include_router(site_settings_routes.router)
app.include_router(routes_products)
app.include_router(routes_category)
app.include_router(routes_warranty)
app.include_router(routes_brand)
app.include_router(routes_condition)
app.include_router(routes_capacity)
app.include_router(social_network_routes.router)
app.include_router(subscriber_routes.router)
app.include_router(banner_upload_routes.router)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

