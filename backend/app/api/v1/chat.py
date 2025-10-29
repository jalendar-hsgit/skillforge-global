from fastapi import APIRouter
from ...schemas.chat import ChatIn, ChatOut

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatOut)
def chat(payload: ChatIn):
    # Stubbed response for now; real AI will be wired later
    return ChatOut(reply=f"I received: {payload.message}. A personalized plan will appear here soon.")
