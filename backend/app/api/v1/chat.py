from fastapi import APIRouter

from ...schemas.chat import ChatIn, ChatOut

router = APIRouter(prefix="/chat", tags=["chat"])


def _extract_message(payload: ChatIn) -> str:
    # Prefer explicit message string; otherwise pull the last user message from chat history
    if payload.message:
        return payload.message

    if payload.messages:
        for msg in reversed(payload.messages):
            if msg.role == "user" and msg.content:
                return msg.content
        # fallback to last message regardless of role
        return payload.messages[-1].content

    return "Hello"


@router.post("", response_model=ChatOut)
def chat(payload: ChatIn):
    content = _extract_message(payload)
    # Stubbed response for now; real AI will be wired later
    return ChatOut(reply=f"I received: {content}. A personalized plan will appear here soon.")
