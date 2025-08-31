from typing import List, Optional, Union
from pydantic import BaseModel

class FileData(BaseModel):
    data: str  # base64 encoded string
    mime_type: str

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: Union[str, List[FileData]]

class LastUserMessage(BaseModel):
    text: str
    files: Optional[List[FileData]] = []

class ChatRequest(BaseModel):
    message: LastUserMessage
    history: List[Message]
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None

class RichChatResponse(BaseModel):
    text_answer: str
    charts: Optional[List[str]] = [] # List of base64 encoded chart images
    error: Optional[str] = None
