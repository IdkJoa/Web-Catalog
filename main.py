from fastapi import FastAPI

from app.router.router_products import router as router_products
from app.router.router_category import router as router_category
from app.router.router_warranty import router as router_warranty
from app.router.router_brand import router as router_brand
from app.router.router_condition import router as router_condition
from app.router.router_capacity import router as router_capacity

app = FastAPI()

app.include_router(router_products)
app.include_router(router_category)
app.include_router(router_warranty)
app.include_router(router_brand)
app.include_router(router_condition)
app.include_router(router_capacity)

