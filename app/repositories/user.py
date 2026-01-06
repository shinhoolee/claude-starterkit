"""
User Repository

사용자 데이터 접근 계층입니다.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
  """
  사용자 Repository

  User 모델에 대한 데이터베이스 작업을 처리합니다.
  """

  def __init__(self):
    """UserRepository 초기화"""
    super().__init__(User)

  def get_by_email(self, db: Session, email: str) -> Optional[User]:
    """
    이메일로 사용자 조회

    Args:
      db: 데이터베이스 세션
      email: 조회할 이메일 주소

    Returns:
      Optional[User]: 조회된 사용자 (없으면 None)
    """
    return self.get_by_field(db, "email", email)

  def get_by_username(self, db: Session, username: str) -> Optional[User]:
    """
    사용자명으로 사용자 조회

    Args:
      db: 데이터베이스 세션
      username: 조회할 사용자명

    Returns:
      Optional[User]: 조회된 사용자 (없으면 None)
    """
    return self.get_by_field(db, "username", username)

  def exists_by_email(self, db: Session, email: str) -> bool:
    """
    이메일 존재 여부 확인

    Args:
      db: 데이터베이스 세션
      email: 확인할 이메일 주소

    Returns:
      bool: 존재하면 True, 없으면 False
    """
    return db.query(User).filter(User.email == email).first() is not None

  def exists_by_username(self, db: Session, username: str) -> bool:
    """
    사용자명 존재 여부 확인

    Args:
      db: 데이터베이스 세션
      username: 확인할 사용자명

    Returns:
      bool: 존재하면 True, 없으면 False
    """
    return db.query(User).filter(User.username == username).first() is not None

  def get_active_users(
    self,
    db: Session,
    skip: int = 0,
    limit: int = 100
  ) -> list[User]:
    """
    활성화된 사용자 목록 조회

    Args:
      db: 데이터베이스 세션
      skip: 건너뛸 레코드 수
      limit: 조회할 최대 레코드 수

    Returns:
      list[User]: 활성화된 사용자 리스트
    """
    return self.get_multi_by_field(
      db,
      "is_active",
      True,
      skip=skip,
      limit=limit
    )

  def get_superusers(self, db: Session) -> list[User]:
    """
    관리자 사용자 목록 조회

    Args:
      db: 데이터베이스 세션

    Returns:
      list[User]: 관리자 사용자 리스트
    """
    return db.query(User).filter(User.is_superuser == True).all()


# 싱글톤 인스턴스
user_repository = UserRepository()
