from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="FastAPI Project",
    description="A simple FastAPI application",
    version="0.1.0"
)


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


# In-memory storage for demonstration
items_db: list[Item] = []


@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Welcome to FastAPI!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    """Get an item by ID with optional query parameter."""
    return {"item_id": item_id, "q": q}


@app.get("/items/")
async def read_items():
    """Get all items."""
    return {"items": items_db, "total": len(items_db)}


@app.post("/items/")
async def create_item(item: Item):
    """Create a new item."""
    items_db.append(item)
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
