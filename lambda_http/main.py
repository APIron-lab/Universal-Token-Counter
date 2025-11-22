from mangum import Mangum
from backend.fastapi_app.main import app

# AWS Lambda 用ハンドラ
handler = Mangum(app)
