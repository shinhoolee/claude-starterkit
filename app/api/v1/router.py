"""
API v1 라우터 통합

모든 v1 API 엔드포인트를 통합하여 하나의 라우터로 관리합니다.
"""
from fastapi import APIRouter

from app.api.v1 import auth, users, health

# API v1 메인 라우터 생성
api_router = APIRouter()

# 헬스체크 엔드포인트
api_router.include_router(
  health.router,
  prefix="/health",
  tags=["Health"]
)

# 인증 엔드포인트
api_router.include_router(
  auth.router,
  prefix="/auth",
  tags=["Auth"]
)

# 사용자 엔드포인트
api_router.include_router(
  users.router,
  prefix="/users",
  tags=["Users"]
)
