"""
Health Check API 엔드포인트

애플리케이션 및 데이터베이스 상태를 확인하는 헬스체크 API를 제공합니다.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db, test_db_connection
from app.schemas.common import HealthCheckResponse, SuccessResponse
from app.utils.response import success_response

router = APIRouter()


@router.get(
  "",
  response_model=SuccessResponse[HealthCheckResponse],
  status_code=status.HTTP_200_OK,
  summary="헬스체크",
  description="애플리케이션 및 데이터베이스 연결 상태를 확인합니다.",
  tags=["Health"]
)
def health_check(db: Session = Depends(get_db)):
  """
  헬스체크

  애플리케이션이 정상적으로 실행 중인지, 데이터베이스 연결이 정상인지 확인합니다.

  Returns:
    - status: 애플리케이션 상태 ("healthy" 또는 "unhealthy")
    - database: 데이터베이스 연결 상태 ("connected" 또는 "disconnected")
  """
  # 데이터베이스 연결 테스트
  db_status = "connected" if test_db_connection() else "disconnected"

  # 헬스체크 응답
  health_data = HealthCheckResponse(
    status="healthy",
    database=db_status
  )

  return success_response(
    data=health_data,
    message="애플리케이션이 정상적으로 실행 중입니다."
  )
