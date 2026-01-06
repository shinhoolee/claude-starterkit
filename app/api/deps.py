"""
API 의존성 (Dependencies)

FastAPI 엔드포인트에서 사용되는 공통 의존성을 정의합니다.
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth import auth_service
from app.core.exceptions import UnauthorizedException, EntityNotFoundException

# HTTP Bearer 토큰 스키마
security = HTTPBearer()


def get_current_user(
  credentials: HTTPAuthorizationCredentials = Depends(security),
  db: Session = Depends(get_db)
) -> User:
  """
  현재 인증된 사용자 조회

  Authorization 헤더의 Bearer 토큰을 검증하고 사용자를 반환합니다.

  Args:
    credentials: HTTP Authorization 헤더 (Bearer 토큰)
    db: 데이터베이스 세션

  Returns:
    User: 인증된 사용자

  Raises:
    HTTPException: 인증 실패 시 401 Unauthorized

  사용 예시:
    @router.get("/me")
    def get_me(current_user: User = Depends(get_current_user)):
        return current_user
  """
  token = credentials.credentials

  try:
    # Access Token 검증 및 사용자 조회
    user = auth_service.verify_access_token(db, token)
    return user
  except (UnauthorizedException, EntityNotFoundException) as e:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail=e.message,
      headers={"WWW-Authenticate": "Bearer"}
    )
  except Exception:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="인증에 실패했습니다.",
      headers={"WWW-Authenticate": "Bearer"}
    )


def get_current_active_user(
  current_user: User = Depends(get_current_user)
) -> User:
  """
  현재 활성화된 사용자 조회

  인증된 사용자가 활성화 상태인지 확인합니다.

  Args:
    current_user: 현재 인증된 사용자

  Returns:
    User: 활성화된 사용자

  Raises:
    HTTPException: 비활성화된 사용자인 경우 403 Forbidden

  사용 예시:
    @router.get("/protected")
    def protected_route(user: User = Depends(get_current_active_user)):
        return {"message": "Protected resource"}
  """
  if not current_user.is_active:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="비활성화된 계정입니다."
    )
  return current_user


def get_current_superuser(
  current_user: User = Depends(get_current_user)
) -> User:
  """
  현재 관리자 사용자 조회

  인증된 사용자가 관리자 권한을 가지고 있는지 확인합니다.

  Args:
    current_user: 현재 인증된 사용자

  Returns:
    User: 관리자 사용자

  Raises:
    HTTPException: 관리자가 아닌 경우 403 Forbidden

  사용 예시:
    @router.delete("/users/{user_id}")
    def delete_user(
        user_id: int,
        admin: User = Depends(get_current_superuser)
    ):
        # 관리자만 사용자 삭제 가능
        pass
  """
  if not current_user.is_superuser:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="관리자 권한이 필요합니다."
    )
  return current_user
