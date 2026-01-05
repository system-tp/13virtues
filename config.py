import os
from dotenv import load_dotenv

# プロジェクト直下の .env ファイルを読み込む
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret_key_123")

# ここがポイント：環境変数 "DATABASE_URL" があればそれを使う
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://postgres:wpekusj9@localhost:5432/virtues" # ← デフォルト（ローカル用）
)