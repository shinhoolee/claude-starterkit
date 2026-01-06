"""
전역 예외 핸들러

모든 예외를 포착하여 표준 형식의 응답으로 변환합니다.
"""
import logging
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import BaseAPIException

logger = logging.getLogger(__name__)


async def base_exception_handler(
  request: Request,
  exc: BaseAPIException
) -> JSONResponse:
  """
  커스텀 예외 핸들러

  BaseAPIException을 상속받은 모든 예외를 처리합니다.
  """
  logger.error(
    f"API 예외 발생: {exc.error_code} - {exc.message}",
    extra={
      "error_code": exc.error_code,
      "status_code": exc.status_code,
      "path": request.url.path,
      "method": request.method,
      "details": exc.details
    }
  )

  return JSONResponse(
    status_code=exc.status_code,
    content={
      "success": False,
      "message": exc.message,
      "error_code": exc.error_code,
      "details": exc.details,
      "data": None
    }
  )


async def validation_exception_handler(
  request: Request,
  exc: RequestValidationError
) -> JSONResponse:
  """
  Pydantic 유효성 검증 실패 핸들러

  FastAPI의 RequestValidationError를 처리하여 표준 형식으로 변환합니다.
  """
  # Pydantic 에러를 읽기 쉬운 형태로 변환
  errors = []
  for error in exc.errors():
    field = " -> ".join(str(loc) for loc in error["loc"])
    message = error["msg"]
    error_type = error["type"]

    errors.append({
      "field": field,
      "message": message,
      "type": error_type
    })

  logger.warning(
    f"유효성 검증 실패: {request.url.path}",
    extra={
      "path": request.url.path,
      "method": request.method,
      "errors": errors
    }
  )

  return JSONResponse(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    content={
      "success": False,
      "message": "요청 데이터 유효성 검증에 실패했습니다.",
      "error_code": "VALIDATION_ERROR",
      "details": {"validation_errors": errors},
      "data": None
    }
  )


async def sqlalchemy_exception_handler(
  request: Request,
  exc: SQLAlchemyError
) -> JSONResponse:
  """
  SQLAlchemy 예외 핸들러

  데이터베이스 관련 예외를 처리합니다.
  """
  logger.error(
    f"데이터베이스 오류: {str(exc)}",
    extra={
      "path": request.url.path,
      "method": request.method,
      "error": str(exc)
    },
    exc_info=True
  )

  return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={
      "success": False,
      "message": "데이터베이스 작업 중 오류가 발생했습니다.",
      "error_code": "DATABASE_ERROR",
      "details": {},
      "data": None
    }
  )


async def general_exception_handler(
  request: Request,
  exc: Exception
) -> JSONResponse:
  """
  일반 예외 핸들러 (최종 안전망)

  처리되지 않은 모든 예외를 포착합니다.
  """
  logger.critical(
    f"처리되지 않은 예외 발생: {str(exc)}",
    extra={
      "path": request.url.path,
      "method": request.method,
      "error": str(exc)
    },
    exc_info=True
  )

  return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={
      "success": False,
      "message": "서버 내부 오류가 발생했습니다.",
      "error_code": "INTERNAL_SERVER_ERROR",
      "details": {},
      "data": None
    }
  )


def register_exception_handlers(app) -> None:
  """
  FastAPI 앱에 예외 핸들러 등록

  사용 예시:
    from fastapi import FastAPI
    from app.middleware.error_handler import register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)
  """
  app.add_exception_handler(BaseAPIException, base_exception_handler)
  app.add_exception_handler(RequestValidationError, validation_exception_handler)
  app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
  app.add_exception_handler(Exception, general_exception_handler)

  logger.info("전역 예외 핸들러가 등록되었습니다.")
