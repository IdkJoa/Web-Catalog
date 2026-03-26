from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.router_products import router as router_products
from app.routes.router_category import router as router_category
from app.routes.router_warranty import router as router_warranty
from app.routes.router_brand import router as router_brand
from app.routes.router_condition import router as router_condition
from app.routes.router_capacity import router as router_capacity
from app.routes import auth_routes, testimonial_routes

app = FastAPI(
    title="Web'Catalog API",
    description="Backend API for managing products and content",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "CMS API is running"}

app.include_router(auth_routes.router)
app.include_router(testimonial_routes.router)
app.include_router(router_products)
app.include_router(router_category)
app.include_router(router_warranty)
app.include_router(router_brand)
app.include_router(router_condition)
app.include_router(router_capacity)

