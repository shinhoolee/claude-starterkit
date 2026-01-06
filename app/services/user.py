"""
User Service

사용자 관련 비즈니스 로직을 처리합니다.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user import user_repository
from app.core.security import hash_password
from app.core.exceptions import (
  EntityNotFoundException,
  DuplicateEntityException,
  ValidationException
)


class UserService:
  """
  사용자 서비스

  사용자 생성, 조회, 수정, 삭제 등의 비즈니스 로직을 처리합니다.
  """

  def __init__(self):
    """UserService 초기화"""
    self.repository = user_repository

  def create_user(self, db: Session, user_in: UserCreate) -> User:
    """
    새 사용자 생성

    Args:
      db: 데이터베이스 세션
      user_in: 사용자 생성 요청 데이터

    Returns:
      User: 생성된 사용자

    Raises:
      DuplicateEntityException: 이메일 또는 사용자명이 이미 존재하는 경우
    """
    # 이메일 중복 체크
    if self.repository.exists_by_email(db, user_in.email):
      raise DuplicateEntityException(
        message=f"이메일 '{user_in.email}'은 이미 사용 중입니다.",
        details={"field": "email", "value": user_in.email}
      )

    # 사용자명 중복 체크
    if self.repository.exists_by_username(db, user_in.username):
      raise DuplicateEntityException(
        message=f"사용자명 '{user_in.username}'은 이미 사용 중입니다.",
        details={"field": "username", "value": user_in.username}
      )

    # 비밀번호 해싱
    hashed_password = hash_password(user_in.password)

    # 사용자 생성
    user_data = {
      "email": user_in.email,
      "username": user_in.username,
      "full_name": user_in.full_name,
      "hashed_password": hashed_password,
      "is_active": True,
      "is_superuser": False
    }

    return self.repository.create(db, user_data)

  def get_user(self, db: Session, user_id: int) -> User:
    """
    사용자 조회

    Args:
      db: 데이터베이스 세션
      user_id: 조회할 사용자 ID

    Returns:
      User: 조회된 사용자

    Raises:
      EntityNotFoundException: 사용자를 찾을 수 없는 경우
    """
    user = self.repository.get_by_id(db, user_id)
    if not user:
      raise EntityNotFoundException(
        message=f"사용자 ID {user_id}를 찾을 수 없습니다.",
        details={"user_id": user_id}
      )
    return user

  def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
    """
    이메일로 사용자 조회

    Args:
      db: 데이터베이스 세션
      email: 조회할 이메일

    Returns:
      Optional[User]: 조회된 사용자 (없으면 None)
    """
    return self.repository.get_by_email(db, email)

  def get_users(
    self,
    db: Session,
    skip: int = 0,
    limit: int = 100
  ) -> List[User]:
    """
    사용자 목록 조회

    Args:
      db: 데이터베이스 세션
      skip: 건너뛸 레코드 수
      limit: 조회할 최대 레코드 수

    Returns:
      List[User]: 사용자 리스트
    """
    return self.repository.get_multi(db, skip=skip, limit=limit)

  def get_users_count(self, db: Session) -> int:
    """
    전체 사용자 수 조회

    Args:
      db: 데이터베이스 세션

    Returns:
      int: 전체 사용자 수
    """
    return self.repository.count(db)

  def update_user(
    self,
    db: Session,
    user_id: int,
    user_in: UserUpdate
  ) -> User:
    """
    사용자 정보 수정

    Args:
      db: 데이터베이스 세션
      user_id: 수정할 사용자 ID
      user_in: 수정할 데이터

    Returns:
      User: 수정된 사용자

    Raises:
      EntityNotFoundException: 사용자를 찾을 수 없는 경우
      DuplicateEntityException: 사용자명이 이미 존재하는 경우
    """
    # 기존 사용자 조회
    user = self.get_user(db, user_id)

    # 사용자명 중복 체크 (변경하는 경우만)
    if user_in.username and user_in.username != user.username:
      if self.repository.exists_by_username(db, user_in.username):
        raise DuplicateEntityException(
          message=f"사용자명 '{user_in.username}'은 이미 사용 중입니다.",
          details={"field": "username", "value": user_in.username}
        )

    # 업데이트 데이터 준비
    update_data = {}
    if user_in.username is not None:
      update_data["username"] = user_in.username
    if user_in.full_name is not None:
      update_data["full_name"] = user_in.full_name
    if user_in.is_active is not None:
      update_data["is_active"] = user_in.is_active
    if user_in.password is not None:
      update_data["hashed_password"] = hash_password(user_in.password)

    return self.repository.update(db, user, update_data)

  def delete_user(self, db: Session, user_id: int) -> User:
    """
    사용자 삭제

    Args:
      db: 데이터베이스 세션
      user_id: 삭제할 사용자 ID

    Returns:
      User: 삭제된 사용자

    Raises:
      EntityNotFoundException: 사용자를 찾을 수 없는 경우
    """
    user = self.repository.delete(db, user_id)
    if not user:
      raise EntityNotFoundException(
        message=f"사용자 ID {user_id}를 찾을 수 없습니다.",
        details={"user_id": user_id}
      )
    return user

  def deactivate_user(self, db: Session, user_id: int) -> User:
    """
    사용자 비활성화 (소프트 삭제)

    Args:
      db: 데이터베이스 세션
      user_id: 비활성화할 사용자 ID

    Returns:
      User: 비활성화된 사용자

    Raises:
      EntityNotFoundException: 사용자를 찾을 수 없는 경우
    """
    user = self.get_user(db, user_id)
    return self.repository.update(db, user, {"is_active": False})


# 싱글톤 인스턴스
user_service = UserService()
