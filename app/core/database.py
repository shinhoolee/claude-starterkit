"""
PostgreSQL 연결 및 SQLAlchemy 세션 관리

FastAPI 의존성 주입을 위한 데이터베이스 세션 제공
"""
import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy 엔진 생성
engine = create_engine(
  settings.DATABASE_URL,
  pool_pre_ping=True,  # 연결 유효성 사전 확인
  echo=settings.DEBUG,  # 개발 환경에서 SQL 쿼리 로그 출력
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(
  autocommit=False,
  autoflush=False,
  bind=engine
)


def get_db() -> Generator[Session, None, None]:
  """
  FastAPI 의존성 주입용 DB 세션 제너레이터

  사용 예시:
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
  """
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


def test_db_connection() -> bool:
  """
  데이터베이스 연결 테스트

  Returns:
    bool: 연결 성공 시 True, 실패 시 False
  """
  try:
    with engine.connect() as conn:
      conn.execute(text("SELECT 1"))
    logger.info("데이터베이스 연결 성공")
    return True
  except SQLAlchemyError as e:
    logger.error(f"데이터베이스 연결 실패: {e}")
    return False
