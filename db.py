from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
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

class DailyInput(Base):
    __tablename__ = "daily_inputs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_kanri.id"))
    date = Column(Date, default=date.today)
    answer = Column(Text)
    today_goal = Column(Text)
    virtue = Column(String(255))
    virtue2 = Column(String(255))
    goal_score = Column(Integer)
    reflection = Column(Text)
    thanks = Column(Text)
    apply_learning = Column(Text)

class MonthlyTheme(Base):
    __tablename__ = "monthly_theme"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    theme_text = Column(String, nullable=False)
    pages = Column(Integer, nullable=True)

class WeeklyQuestion(Base):
    __tablename__ = "weekly_question"

    id = Column(Integer, primary_key=True)
    week_start_date = Column(Date, nullable=False)
    question_text = Column(String, nullable=False)

    pages = Column(Integer, nullable=False, default=1)

# ★★ これがないとテーブル作られない ★★
Base.metadata.create_all(bind=engine)

