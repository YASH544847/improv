from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    prompt: str

    class Config:
        str_strip_whitespace = True
        min_anystr_length = 1


class PromptResponse(BaseModel):
    improved_prompt: str
    error: Optional[str] = None
