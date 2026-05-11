from sqlalchemy import Column, Integer, String, Date, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, default="Turin")
    cuisine = Column(String, default="Restaurant")
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    logo_url = Column(String, default="/joeai-logo.svg")
    status = Column(String, default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String)
    first_visit = Column(Date)
    last_visit = Column(Date)
    total_spent = Column(Float, default=0)
    visit_count = Column(Integer, default=0)
    favorite_item = Column(String)
    tags = Column(String)
    notes = Column(Text)
    opted_in_whatsapp = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, default="Other")
    price = Column(Float, default=0)
    cost = Column(Float, default=0)
    active = Column(Boolean, default=True)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    channel = Column(String, default="in_house")
    total_amount = Column(Float, default=0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    item_name = Column(String, nullable=False)
    category = Column(String)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0)
    unit_cost = Column(Float, default=0)
    line_total = Column(Float, default=0)


class AiMessage(Base):
    __tablename__ = "ai_messages"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
