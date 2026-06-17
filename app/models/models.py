import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import HttpUrl
from sqlalchemy import String, Text, Numeric, ForeignKey, DateTime, Boolean, Integer, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    meta_title: Mapped[Optional[str]] = mapped_column(String(100))
    meta_description: Mapped[Optional[str]] = mapped_column(String(160))
    meta_keywords: Mapped[Optional[str]] = mapped_column(String(255))

    products: Mapped[List["Product"]] = relationship(back_populates="category")


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[List["Product"]] = relationship(back_populates="brand")


class Condition(Base):
    __tablename__ = "conditions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[List["Product"]] = relationship(back_populates="condition")


class Warranty(Base):
    __tablename__ = "warranties"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    duration: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[List["Product"]] = relationship(back_populates="warranty")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))
    brand_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brands.id"))
    condition_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conditions.id"))
    warranty_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warranties.id"))

    name: Mapped[str] = mapped_column(String(255))
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    model_name: Mapped[Optional[str]] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Numeric(18, 4))
    sale_price: Mapped[Optional[float]] = mapped_column(Numeric(18, 4))
    stock_status: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(),
                                                 server_default=func.now())
    meta_title: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "My Store | Home"
    meta_description: Mapped[Optional[str]] = mapped_column(String(160))  # Best practice length
    meta_keywords: Mapped[Optional[str]] = mapped_column(String(255))

    category: Mapped["Category"] = relationship(back_populates="products")
    brand: Mapped["Brand"] = relationship(back_populates="products")
    condition: Mapped["Condition"] = relationship(back_populates="products")
    warranty: Mapped["Warranty"] = relationship(back_populates="products")
    capacities: Mapped[List["Capacity"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class Capacity(Base):
    __tablename__ = "capacities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    capacity: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product: Mapped["Product"] = relationship(back_populates="capacities")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[Optional[str]] = mapped_column(String(255))
    image_url: Mapped[str] = mapped_column(String(255))
    link: Mapped[Optional[str]] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(),
                                                 server_default=func.now())


class Testimonial(Base):
    __tablename__ = "testimonials"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    comment: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    whatsapp: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    open_time: Mapped[Optional[str]] = mapped_column(String(5))
    close_time: Mapped[Optional[str]] = mapped_column(String(5))
    #SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(100))
    meta_description: Mapped[Optional[str]] = mapped_column(String(160))
    meta_keywords: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))


class SocialNetwork(Base):
    __tablename__ = "social_networks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))


class Subscriber(Base):
    __tablename__ = "subscribers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    registration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())