from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.routes_products import router as routes_products
from app.routes.routes_category import router as routes_category
from app.routes.routes_warranty import router as routes_warranty
from app.routes.routes_brand import router as routes_brand
from app.routes.routes_condition import router as routes_condition
from app.routes.routes_capacity import router as routes_capacity
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
app.include_router(routes_products)
app.include_router(routes_category)
app.include_router(routes_warranty)
app.include_router(routes_brand)
app.include_router(routes_condition)
app.include_router(routes_capacity)

