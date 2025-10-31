from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI!"}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_read_item():
    """Test reading an item by ID."""
    response = client.get("/items/42?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "test"}


def test_read_item_no_query():
    """Test reading an item without query parameter."""
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "q": None}


def test_create_item():
    """Test creating a new item."""
    item_data = {
        "name": "Test Item",
        "description": "A test item",
        "price": 10.5,
        "tax": 1.5
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 10.5
    assert data["price_with_tax"] == 12.0


def test_create_item_no_tax():
    """Test creating an item without tax."""
    item_data = {
        "name": "Simple Item",
        "price": 5.0
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Simple Item"
    assert data["price"] == 5.0
    assert "price_with_tax" not in data


def test_read_all_items():
    """Test getting all items."""
    # Create a few items first
    item1 = {"name": "Item 1", "price": 10.0}
    item2 = {"name": "Item 2", "price": 20.0, "tax": 2.0}
    
    client.post("/items/", json=item1)
    client.post("/items/", json=item2)
    
    # Get all items
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
