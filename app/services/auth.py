"""
Auth Service

인증 관련 비즈니스 로직을 처리합니다.
"""
from typing import Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user import user_repository
from app.core.security import (
  verify_password,
  create_access_token,
  create_refresh_token,
  get_token_subject,
  verify_token_type
)
from app.core.exceptions import (
  UnauthorizedException,
  EntityNotFoundException
)


class AuthService:
  """
  인증 서비스

  로그인, 토큰 생성/검증 등의 비즈니스 로직을 처리합니다.
  """

  def __init__(self):
    """AuthService 초기화"""
    self.repository = user_repository

  def authenticate(
    self,
    db: Session,
    email: str,
    password: str
  ) -> User:
    """
    사용자 인증

    이메일과 비밀번호를 검증하여 사용자를 인증합니다.

    Args:
      db: 데이터베이스 세션
      email: 이메일 주소
      password: 비밀번호

    Returns:
      User: 인증된 사용자

    Raises:
      UnauthorizedException: 인증 실패 (이메일 또는 비밀번호 불일치)
    """
    # 이메일로 사용자 조회
    user = self.repository.get_by_email(db, email)
    if not user:
      raise UnauthorizedException(
        message="이메일 또는 비밀번호가 일치하지 않습니다.",
        details={"email": email}
      )

    # 비밀번호 검증
    if not verify_password(password, user.hashed_password):
      raise UnauthorizedException(
        message="이메일 또는 비밀번호가 일치하지 않습니다.",
        details={"email": email}
      )

    # 계정 활성화 상태 확인
    if not user.is_active:
      raise UnauthorizedException(
        message="비활성화된 계정입니다.",
        details={"email": email}
      )

    return user

  def login(
    self,
    db: Session,
    email: str,
    password: str
  ) -> Tuple[str, str]:
    """
    로그인

    사용자를 인증하고 Access Token 및 Refresh Token을 발급합니다.

    Args:
      db: 데이터베이스 세션
      email: 이메일 주소
      password: 비밀번호

    Returns:
      Tuple[str, str]: (access_token, refresh_token)

    Raises:
      UnauthorizedException: 인증 실패
    """
    # 사용자 인증
    user = self.authenticate(db, email, password)

    # 토큰 생성 (subject로 사용자 이메일 사용)
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)

    return access_token, refresh_token

  def refresh_access_token(
    self,
    db: Session,
    refresh_token: str
  ) -> str:
    """
    Access Token 갱신

    Refresh Token을 검증하고 새로운 Access Token을 발급합니다.

    Args:
      db: 데이터베이스 세션
      refresh_token: Refresh Token

    Returns:
      str: 새로운 Access Token

    Raises:
      UnauthorizedException: Refresh Token 검증 실패
      EntityNotFoundException: 사용자를 찾을 수 없는 경우
    """
    # Refresh Token 타입 검증
    if not verify_token_type(refresh_token, "refresh"):
      raise UnauthorizedException(
        message="유효하지 않은 Refresh Token입니다.",
        details={"error": "invalid_token_type"}
      )

    # 토큰에서 이메일 추출
    email = get_token_subject(refresh_token)
    if not email:
      raise UnauthorizedException(
        message="유효하지 않은 Refresh Token입니다.",
        details={"error": "invalid_token"}
      )

    # 사용자 존재 여부 및 활성화 상태 확인
    user = self.repository.get_by_email(db, email)
    if not user:
      raise EntityNotFoundException(
        message="사용자를 찾을 수 없습니다.",
        details={"email": email}
      )

    if not user.is_active:
      raise UnauthorizedException(
        message="비활성화된 계정입니다.",
        details={"email": email}
      )

    # 새로운 Access Token 발급
    access_token = create_access_token(subject=user.email)

    return access_token

  def verify_access_token(
    self,
    db: Session,
    access_token: str
  ) -> User:
    """
    Access Token 검증

    Access Token을 검증하고 해당 사용자를 반환합니다.

    Args:
      db: 데이터베이스 세션
      access_token: Access Token

    Returns:
      User: 인증된 사용자

    Raises:
      UnauthorizedException: Access Token 검증 실패
      EntityNotFoundException: 사용자를 찾을 수 없는 경우
    """
    # Access Token 타입 검증
    if not verify_token_type(access_token, "access"):
      raise UnauthorizedException(
        message="유효하지 않은 Access Token입니다.",
        details={"error": "invalid_token_type"}
      )

    # 토큰에서 이메일 추출
    email = get_token_subject(access_token)
    if not email:
      raise UnauthorizedException(
        message="유효하지 않은 Access Token입니다.",
        details={"error": "invalid_token"}
      )

    # 사용자 조회
    user = self.repository.get_by_email(db, email)
    if not user:
      raise EntityNotFoundException(
        message="사용자를 찾을 수 없습니다.",
        details={"email": email}
      )

    # 계정 활성화 상태 확인
    if not user.is_active:
      raise UnauthorizedException(
        message="비활성화된 계정입니다.",
        details={"email": email}
      )

    return user


# 싱글톤 인스턴스
auth_service = AuthService()
