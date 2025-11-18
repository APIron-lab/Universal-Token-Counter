from fastapi import FastAPI
from .router import router
from .handlers import register_exception_handlers

app = FastAPI(
    title="Universal Token Counter API",
    version="0.1.0",
    description="High-precision multilingual token counting API."
)

# ルーター登録
app.include_router(router, prefix="/utc/v0")

# エラーハンドラ登録
register_exception_handlers(app)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

