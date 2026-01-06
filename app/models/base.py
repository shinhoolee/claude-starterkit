"""
SQLAlchemy Base 모델 및 공통 필드 정의

모든 데이터베이스 모델이 상속할 Base 클래스와 공통 필드를 제공합니다.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base, declared_attr

# Base 클래스 생성
Base = declarative_base()


class TimestampMixin:
  """생성/수정 시각 자동 관리 믹스인"""

  created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
  updated_at = Column(
    DateTime,
    default=datetime.utcnow,
    onupdate=datetime.utcnow,
    nullable=False
  )


class BaseModel(Base, TimestampMixin):
  """
  모든 모델의 기본 클래스

  공통 필드:
  - id: 기본 키
  - created_at: 생성 시각
  - updated_at: 수정 시각
  """
  __abstract__ = True

  id = Column(Integer, primary_key=True, index=True, autoincrement=True)

  @declared_attr
  def __tablename__(cls) -> str:
    """테이블 이름을 클래스 이름의 소문자 복수형으로 자동 생성"""
    return cls.__name__.lower() + "s"
