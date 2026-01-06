"""
User 모델

사용자 정보를 저장하는 SQLAlchemy 모델입니다.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
  """
  사용자 모델

  Attributes:
    id: 사용자 고유 ID (Primary Key)
    email: 이메일 (고유, 인덱스)
    username: 사용자명 (고유, 인덱스)
    hashed_password: 해싱된 비밀번호
    full_name: 전체 이름 (선택사항)
    is_active: 계정 활성화 상태
    is_superuser: 관리자 여부
    created_at: 생성 일시
    updated_at: 수정 일시
  """

  __tablename__ = "users"

  id = Column(
    Integer,
    primary_key=True,
    index=True,
    autoincrement=True,
    comment="사용자 고유 ID"
  )

  email = Column(
    String(255),
    unique=True,
    index=True,
    nullable=False,
    comment="이메일 (로그인 ID)"
  )

  username = Column(
    String(50),
    unique=True,
    index=True,
    nullable=False,
    comment="사용자명"
  )

  hashed_password = Column(
    String(255),
    nullable=False,
    comment="해싱된 비밀번호"
  )

  full_name = Column(
    String(100),
    nullable=True,
    comment="전체 이름"
  )

  is_active = Column(
    Boolean,
    default=True,
    nullable=False,
    comment="계정 활성화 상태"
  )

  is_superuser = Column(
    Boolean,
    default=False,
    nullable=False,
    comment="관리자 여부"
  )

  created_at = Column(
    DateTime,
    default=datetime.utcnow,
    nullable=False,
    comment="생성 일시"
  )

  updated_at = Column(
    DateTime,
    default=datetime.utcnow,
    onupdate=datetime.utcnow,
    nullable=False,
    comment="수정 일시"
  )

  def __repr__(self) -> str:
    """객체 문자열 표현"""
    return f"<User(id={self.id}, email={self.email}, username={self.username})>"
