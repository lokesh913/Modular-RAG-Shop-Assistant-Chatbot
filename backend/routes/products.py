from fastapi import APIRouter, HTTPException
from backend.db.mysql import get_db_connection

router = APIRouter()

@router.get("/products")
def get_products():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        cursor.close()
        db.close()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")