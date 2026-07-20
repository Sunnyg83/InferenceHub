from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question")
    stream: bool = Field(default=False, description="Stream tokens via SSE if true")


class ChatResponse(BaseModel):
    answer: str
    cache_hit: bool = False
