from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    improved_prompt: str
