import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret_key_123")

# SQLAlchemy の接続文字列はクラス外に定義する（超重要）
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:wpekusj9@localhost:5432/virtues"
)
