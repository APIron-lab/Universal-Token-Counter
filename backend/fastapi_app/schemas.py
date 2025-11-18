from pydantic import BaseModel

class TokenCountRequest(BaseModel):
    model: str
    text: str

class TokenCountResult(BaseModel):
    model: str
    encoding: str
    char_count: int
    token_count: int
    token_per_char: float

class TokenCountMeta(BaseModel):
    input_language: str
    input_size_bytes: int
    token_density: float
    model_family: str
    processing_time_ms: float
    utc_timestamp: str
    version: str

class TokenCountSuccessResponse(BaseModel):
    result: TokenCountResult
    meta: TokenCountMeta

