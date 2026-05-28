from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.gemini_chain import generate_response

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    history: list[str] = []

@router.post("/chat")
def chat(request: ChatRequest):
    try:
        response, history = generate_response(request.query, request.history)
        return {"response": response, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Service error: {str(e)}")