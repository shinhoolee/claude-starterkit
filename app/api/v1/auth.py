"""
Auth API 엔드포인트

인증 관련 API (로그인, 토큰 갱신, 현재 사용자 조회)를 제공합니다.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.auth import (
  LoginRequest,
  TokenResponse,
  RefreshTokenRequest,
  AccessTokenResponse
)
from app.schemas.user import UserResponse
from app.schemas.common import SuccessResponse
from app.services.auth import auth_service
from app.models.user import User
from app.utils.response import success_response

router = APIRouter()


@router.post(
  "/login",
  response_model=SuccessResponse[TokenResponse],
  status_code=status.HTTP_200_OK,
  summary="로그인",
  description="이메일과 비밀번호로 로그인하여 Access Token과 Refresh Token을 발급받습니다."
)
def login(
  login_data: LoginRequest,
  db: Session = Depends(get_db)
):
  """
  로그인

  이메일과 비밀번호를 검증하고 JWT 토큰을 발급합니다.
  """
  # 로그인 처리
  access_token, refresh_token = auth_service.login(
    db,
    email=login_data.email,
    password=login_data.password
  )

  # 응답 데이터 생성
  token_data = TokenResponse(
    access_token=access_token,
    refresh_token=refresh_token,
    token_type="bearer"
  )

  return success_response(
    data=token_data,
    message="로그인에 성공했습니다."
  )


@router.post(
  "/refresh",
  response_model=SuccessResponse[AccessTokenResponse],
  status_code=status.HTTP_200_OK,
  summary="토큰 갱신",
  description="Refresh Token을 사용하여 새로운 Access Token을 발급받습니다."
)
def refresh_token(
  refresh_data: RefreshTokenRequest,
  db: Session = Depends(get_db)
):
  """
  Access Token 갱신

  Refresh Token을 검증하고 새로운 Access Token을 발급합니다.
  """
  # Access Token 갱신
  access_token = auth_service.refresh_access_token(
    db,
    refresh_token=refresh_data.refresh_token
  )

  # 응답 데이터 생성
  token_data = AccessTokenResponse(
    access_token=access_token,
    token_type="bearer"
  )

  return success_response(
    data=token_data,
    message="토큰이 갱신되었습니다."
  )


@router.get(
  "/me",
  response_model=SuccessResponse[UserResponse],
  status_code=status.HTTP_200_OK,
  summary="현재 사용자 정보 조회",
  description="인증된 사용자의 정보를 조회합니다. (인증 필요)"
)
def get_current_user_info(
  current_user: User = Depends(get_current_user)
):
  """
  현재 사용자 정보 조회

  Access Token으로 인증된 사용자의 정보를 반환합니다.
  """
  return success_response(
    data=UserResponse.model_validate(current_user),
    message="사용자 정보 조회 성공"
  )
