from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from config import SQLALCHEMY_DATABASE_URL
from datetime import date

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "user_kanri"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    name_kanji = Column(String(50), nullable=False)
    name_kana = Column(String(50))
    password_hash = Column(String(255), nullable=False)

    # 追加カラム
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)

    # DailyInput リレーション
    daily_inputs = relationship("DailyInput", back_populates="user")


class DailyInput(Base):
    __tablename__ = "daily_inputs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ★ テーブル名を "user_kanri.id" に修正
    user_id = Column(Integer, ForeignKey("user_kanri.id"))

    date = Column(Date, default=date.today)
    answer = Column(Text)
    today_goal = Column(Text)
    virtue = Column(String(255))
    goal_score = Column(Integer)
    reflection = Column(Text)
    thanks = Column(Text)
    apply_learning = Column(Text)

    # リレーション
    user = relationship("User", back_populates="daily_inputs")


# ★ テーブル作成
Base.metadata.create_all(bind=engine)
