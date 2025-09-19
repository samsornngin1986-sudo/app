from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Marq' E Donuts Management System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class CategoryType(str, Enum):
    DONUTS = "donuts"
    TACOS = "tacos"
    KOLACHES = "kolaches"
    CROISSANTS = "croissants"
    COFFEE = "coffee"
    BEVERAGES = "beverages"

class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"

class EmployeeRole(str, Enum):
    MANAGER = "manager"
    CASHIER = "cashier"
    BAKER = "baker"
    PREP_COOK = "prep_cook"

# Data Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: CategoryType
    price: float
    cost: float
    description: Optional[str] = None
    ingredients: List[str] = []
    prep_time: int = 0  # in minutes
    is_available: bool = True
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    name: str
    category: CategoryType
    price: float
    cost: float
    description: Optional[str] = None
    ingredients: List[str] = []
    prep_time: int = 0
    is_available: bool = True
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[CategoryType] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    prep_time: Optional[int] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None

class InventoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    quantity: int
    min_threshold: int = 10
    max_capacity: int = 100
    status: StockStatus
    last_restocked: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expiry_date: Optional[datetime] = None

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    min_threshold: Optional[int] = None
    max_capacity: Optional[int] = None

class Sale(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    items: List[Dict[str, Any]]  # [{"product_id": str, "quantity": int, "price": float}]
    total_amount: float
    payment_method: str = "cash"
    customer_name: Optional[str] = None
    employee_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    order_type: str = "dine_in"  # dine_in, takeout, catering

class SaleCreate(BaseModel):
    items: List[Dict[str, Any]]
    total_amount: float
    payment_method: str = "cash"
    customer_name: Optional[str] = None
    employee_id: Optional[str] = None
    order_type: str = "dine_in"

class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: EmployeeRole
    email: Optional[str] = None
    phone: Optional[str] = None
    hourly_wage: float = 15.0
    hire_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class EmployeeCreate(BaseModel):
    name: str
    role: EmployeeRole
    email: Optional[str] = None
    phone: Optional[str] = None
    hourly_wage: float = 15.0

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    total_orders: int = 0
    total_spent: float = 0.0
    loyalty_points: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

# Helper Functions
def update_stock_status(quantity: int, min_threshold: int) -> StockStatus:
    if quantity <= 0:
        return StockStatus.OUT_OF_STOCK
    elif quantity <= min_threshold:
        return StockStatus.LOW_STOCK
    else:
        return StockStatus.IN_STOCK

# Product Routes
@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    product_dict = product.dict()
    product_obj = Product(**product_dict)
    await db.products.insert_one(product_obj.dict())
    
    # Create inventory entry for new product
    inventory_item = InventoryItem(
        product_id=product_obj.id,
        quantity=0,
        status=StockStatus.OUT_OF_STOCK
    )
    await db.inventory.insert_one(inventory_item.dict())
    
    return product_obj

@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[CategoryType] = None):
    query = {}
    if category:
        query["category"] = category
    products = await db.products.find(query).to_list(1000)
    return [Product(**product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate):
    update_data = {k: v for k, v in product_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.products.update_one(
        {"id": product_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated_product = await db.products.find_one({"id": product_id})
    return Product(**updated_product)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Also delete inventory entry
    await db.inventory.delete_one({"product_id": product_id})
    return {"message": "Product deleted successfully"}

# Inventory Routes
@api_router.get("/inventory", response_model=List[InventoryItem])
async def get_inventory():
    inventory = await db.inventory.find().to_list(1000)
    return [InventoryItem(**item) for item in inventory]

@api_router.get("/inventory/{product_id}", response_model=InventoryItem)
async def get_inventory_item(product_id: str):
    item = await db.inventory.find_one({"product_id": product_id})
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return InventoryItem(**item)

@api_router.put("/inventory/{product_id}", response_model=InventoryItem)
async def update_inventory(product_id: str, update: InventoryUpdate):
    current_item = await db.inventory.find_one({"product_id": product_id})
    if not current_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    
    # Update stock status if quantity changed
    if "quantity" in update_data:
        min_threshold = update_data.get("min_threshold", current_item["min_threshold"])
        update_data["status"] = update_stock_status(update_data["quantity"], min_threshold)
        update_data["last_restocked"] = datetime.now(timezone.utc)
    
    await db.inventory.update_one(
        {"product_id": product_id},
        {"$set": update_data}
    )
    
    updated_item = await db.inventory.find_one({"product_id": product_id})
    return InventoryItem(**updated_item)

@api_router.get("/inventory/alerts/low-stock")
async def get_low_stock_alerts():
    low_stock_items = await db.inventory.find({
        "status": {"$in": [StockStatus.LOW_STOCK, StockStatus.OUT_OF_STOCK]}
    }).to_list(1000)
    
    alerts = []
    for item in low_stock_items:
        product = await db.products.find_one({"id": item["product_id"]})
        if product:
            alerts.append({
                "product_name": product["name"],
                "product_id": item["product_id"],
                "current_quantity": item["quantity"],
                "min_threshold": item["min_threshold"],
                "status": item["status"]
            })
    
    return alerts

# Sales Routes
@api_router.post("/sales", response_model=Sale)
async def create_sale(sale: SaleCreate):
    sale_dict = sale.dict()
    sale_obj = Sale(**sale_dict)
    
    # Update inventory for sold items
    for item in sale_obj.items:
        inventory_item = await db.inventory.find_one({"product_id": item["product_id"]})
        if inventory_item:
            new_quantity = max(0, inventory_item["quantity"] - item["quantity"])
            new_status = update_stock_status(new_quantity, inventory_item["min_threshold"])
            
            await db.inventory.update_one(
                {"product_id": item["product_id"]},
                {"$set": {"quantity": new_quantity, "status": new_status}}
            )
    
    # Update customer data if provided
    if sale_obj.customer_name:
        customer = await db.customers.find_one({"name": sale_obj.customer_name})
        if customer:
            await db.customers.update_one(
                {"id": customer["id"]},
                {
                    "$inc": {
                        "total_orders": 1,
                        "total_spent": sale_obj.total_amount,
                        "loyalty_points": int(sale_obj.total_amount)
                    }
                }
            )
    
    await db.sales.insert_one(sale_obj.dict())
    return sale_obj

@api_router.get("/sales", response_model=List[Sale])
async def get_sales(limit: int = 100):
    sales = await db.sales.find().sort("timestamp", -1).limit(limit).to_list(limit)
    return [Sale(**sale) for sale in sales]

@api_router.get("/sales/analytics/daily")
async def get_daily_analytics():
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Daily sales
    daily_sales = await db.sales.find({
        "timestamp": {"$gte": today}
    }).to_list(1000)
    
    total_revenue = sum(sale["total_amount"] for sale in daily_sales)
    total_orders = len(daily_sales)
    
    # Popular items
    item_counts = {}
    for sale in daily_sales:
        for item in sale["items"]:
            product_id = item["product_id"]
            quantity = item["quantity"]
            if product_id in item_counts:
                item_counts[product_id] += quantity
            else:
                item_counts[product_id] = quantity
    
    # Get product names for popular items
    popular_items = []
    for product_id, count in sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        product = await db.products.find_one({"id": product_id})
        if product:
            popular_items.append({
                "name": product["name"],
                "quantity_sold": count,
                "category": product["category"]
            })
    
    return {
        "date": today.isoformat(),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order_value": total_revenue / total_orders if total_orders > 0 else 0,
        "popular_items": popular_items
    }

@api_router.get("/sales/analytics/category")
async def get_category_analytics():
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    daily_sales = await db.sales.find({
        "timestamp": {"$gte": today}
    }).to_list(1000)
    
    category_stats = {}
    
    for sale in daily_sales:
        for item in sale["items"]:
            product = await db.products.find_one({"id": item["product_id"]})
            if product:
                category = product["category"]
                if category not in category_stats:
                    category_stats[category] = {
                        "revenue": 0,
                        "quantity": 0,
                        "orders": 0
                    }
                category_stats[category]["revenue"] += item["price"] * item["quantity"]
                category_stats[category]["quantity"] += item["quantity"]
                category_stats[category]["orders"] += 1
    
    return category_stats

# Employee Routes
@api_router.post("/employees", response_model=Employee)
async def create_employee(employee: EmployeeCreate):
    employee_dict = employee.dict()
    employee_obj = Employee(**employee_dict)
    await db.employees.insert_one(employee_obj.dict())
    return employee_obj

@api_router.get("/employees", response_model=List[Employee])
async def get_employees():
    employees = await db.employees.find({"is_active": True}).to_list(1000)
    return [Employee(**employee) for employee in employees]

# Customer Routes
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_dict = customer.dict()
    customer_obj = Customer(**customer_dict)
    await db.customers.insert_one(customer_obj.dict())
    return customer_obj

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find().sort("total_spent", -1).to_list(1000)
    return [Customer(**customer) for customer in customers]

# Dashboard Routes
@api_router.get("/dashboard/overview")
async def get_dashboard_overview():
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Today's sales
    daily_sales = await db.sales.find({"timestamp": {"$gte": today}}).to_list(1000)
    today_revenue = sum(sale["total_amount"] for sale in daily_sales)
    today_orders = len(daily_sales)
    
    # Inventory alerts
    low_stock_count = await db.inventory.count_documents({
        "status": {"$in": [StockStatus.LOW_STOCK, StockStatus.OUT_OF_STOCK]}
    })
    
    # Total products
    total_products = await db.products.count_documents({})
    
    # Total customers
    total_customers = await db.customers.count_documents({})
    
    # Active employees
    active_employees = await db.employees.count_documents({"is_active": True})
    
    return {
        "today_revenue": today_revenue,
        "today_orders": today_orders,
        "low_stock_alerts": low_stock_count,
        "total_products": total_products,
        "total_customers": total_customers,
        "active_employees": active_employees,
        "average_order_value": today_revenue / today_orders if today_orders > 0 else 0
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()