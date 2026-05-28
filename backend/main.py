import os
import time
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import chat, products
from backend.db.mysql import get_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize and seed the database on startup!
    try:
        print("🔍 Checking database schema and seeding...", flush=True)
        db = None
        # Retry connection 10 times to let managed cloud database boot up fully
        for attempt in range(10):
            try:
                db = get_db_connection()
                break
            except Exception as conn_err:
                print(f"⌛ Waiting for MySQL database to be ready (attempt {attempt+1}/10): {conn_err}", flush=True)
                time.sleep(3)
        
        if db is None:
            raise Exception("Could not connect to MySQL database after 10 attempts.")
            
        cursor = db.cursor()
        
        # Create products table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            ProductID INT PRIMARY KEY,
            ProductName VARCHAR(255) NOT NULL,
            ProductBrand VARCHAR(255),
            Gender VARCHAR(50),
            Price DECIMAL(10, 2),
            Description TEXT,
            PrimaryColor VARCHAR(50)
        )
        """)
        db.commit()
        
        # Check if table is empty
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("🌱 Table is empty! Ingesting products catalog from CSV...", flush=True)
            csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "shop-product-catalog.csv")
            if os.path.exists(csv_path):
                data = pd.read_csv(csv_path)
                for index, row in data.iterrows():
                    sql = """
                    INSERT INTO products (ProductID, ProductName, ProductBrand, Gender, Price, Description, PrimaryColor)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, tuple(row))
                db.commit()
                print(f"✅ Ingested {len(data)} products successfully!", flush=True)
            else:
                print(f"⚠️ CSV file not found at {csv_path}", flush=True)
        else:
            print(f"✅ Database already has {count} products. Skipping seeding.", flush=True)
            
        cursor.close()
        db.close()
    except Exception as e:
        print(f"⚠️ Database auto-initialization skipped/failed: {e}", flush=True)
    
    yield

app = FastAPI(title="Shop Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(products.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Shop Assistant API is running"}