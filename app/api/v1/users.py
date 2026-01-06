"""
Users API 엔드포인트

사용자 관련 API (회원가입, 조회, 수정, 삭제)를 제공합니다.
"""
from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import SuccessResponse, PaginatedResponse
from app.services.user import user_service
from app.models.user import User
from app.utils.response import (
  success_response,
  created_response,
  no_content_response,
  paginated_response
)

router = APIRouter()


@router.post(
  "",
  response_model=SuccessResponse[UserResponse],
  status_code=status.HTTP_201_CREATED,
  summary="회원가입",
  description="새로운 사용자를 생성합니다. (인증 불필요)"
)
def create_user(
  user_in: UserCreate,
  db: Session = Depends(get_db)
):
  """
  회원가입

  이메일, 사용자명, 비밀번호로 새로운 사용자를 생성합니다.
  """
  # 사용자 생성
  user = user_service.create_user(db, user_in)

  return created_response(
    data=UserResponse.model_validate(user),
    message="회원가입이 완료되었습니다."
  )


@router.get(
  "",
  response_model=PaginatedResponse[List[UserResponse]],
  status_code=status.HTTP_200_OK,
  summary="사용자 목록 조회",
  description="사용자 목록을 페이지네이션으로 조회합니다. (인증 필요)"
)
def get_users(
  page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
  page_size: int = Query(20, ge=1, le=100, description="페이지당 항목 수 (1-100)"),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  """
  사용자 목록 조회

  페이지네이션을 적용하여 사용자 목록을 조회합니다.
  """
  # 페이지네이션 계산
  skip = (page - 1) * page_size

  # 사용자 목록 조회
  users = user_service.get_users(db, skip=skip, limit=page_size)
  total = user_service.get_users_count(db)

  # 응답 데이터 변환
  users_response = [UserResponse.model_validate(user) for user in users]

  return paginated_response(
    data=users_response,
    total=total,
    page=page,
    page_size=page_size,
    message="사용자 목록 조회 성공"
  )


@router.get(
  "/{user_id}",
  response_model=SuccessResponse[UserResponse],
  status_code=status.HTTP_200_OK,
  summary="사용자 조회",
  description="특정 사용자의 정보를 조회합니다. (인증 필요)"
)
def get_user(
  user_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  """
  사용자 조회

  사용자 ID로 특정 사용자의 정보를 조회합니다.
  """
  user = user_service.get_user(db, user_id)

  return success_response(
    data=UserResponse.model_validate(user),
    message="사용자 조회 성공"
  )


@router.put(
  "/{user_id}",
  response_model=SuccessResponse[UserResponse],
  status_code=status.HTTP_200_OK,
  summary="사용자 수정",
  description="사용자 정보를 수정합니다. (본인 또는 관리자만 가능)"
)
def update_user(
  user_id: int,
  user_in: UserUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  """
  사용자 정보 수정

  본인 또는 관리자만 사용자 정보를 수정할 수 있습니다.
  """
  # 권한 체크: 본인 또는 관리자만 수정 가능
  if current_user.id != user_id and not current_user.is_superuser:
    from app.core.exceptions import ForbiddenException
    raise ForbiddenException(
      message="자신의 정보만 수정할 수 있습니다.",
      details={"user_id": user_id, "current_user_id": current_user.id}
    )

  # 사용자 정보 수정
  user = user_service.update_user(db, user_id, user_in)

  return success_response(
    data=UserResponse.model_validate(user),
    message="사용자 정보가 수정되었습니다."
  )


@router.delete(
  "/{user_id}",
  response_model=SuccessResponse[None],
  status_code=status.HTTP_200_OK,
  summary="사용자 삭제",
  description="사용자를 삭제합니다. (관리자만 가능)"
)
def delete_user(
  user_id: int,
  db: Session = Depends(get_db),
  admin: User = Depends(get_current_superuser)
):
  """
  사용자 삭제

  관리자만 사용자를 삭제할 수 있습니다.
  """
  # 사용자 삭제
  user_service.delete_user(db, user_id)

  return no_content_response(
    message=f"사용자 ID {user_id}가 삭제되었습니다."
  )
