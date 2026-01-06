"""
공통 응답 스키마

표준 API 응답 형식을 정의합니다.
모든 API 응답은 일관된 구조를 따릅니다.
"""
from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel, Field

# 제네릭 타입 변수 (응답 데이터 타입)
T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
  """
  기본 API 응답 스키마

  모든 API 응답의 기본 구조를 정의합니다.

  Attributes:
    success: 요청 성공 여부
    message: 응답 메시지
    data: 응답 데이터 (제네릭 타입)
    error_code: 에러 코드 (에러 발생 시)
    details: 추가 세부 정보 (에러 발생 시)
  """

  success: bool = Field(
    description="요청 성공 여부"
  )
  message: str = Field(
    description="응답 메시지"
  )
  data: Optional[T] = Field(
    default=None,
    description="응답 데이터"
  )
  error_code: Optional[str] = Field(
    default=None,
    description="에러 코드"
  )
  details: Optional[Dict[str, Any]] = Field(
    default=None,
    description="추가 세부 정보"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "success": True,
        "message": "요청이 성공적으로 처리되었습니다.",
        "data": {},
        "error_code": None,
        "details": None
      }
    }


class SuccessResponse(BaseResponse[T], Generic[T]):
  """
  성공 응답 스키마

  성공적인 요청에 대한 응답입니다.
  """

  success: bool = Field(default=True)
  error_code: Optional[str] = Field(default=None)
  details: Optional[Dict[str, Any]] = Field(default=None)


class ErrorResponse(BaseResponse[None]):
  """
  에러 응답 스키마

  실패한 요청에 대한 응답입니다.
  """

  success: bool = Field(default=False)
  data: None = Field(default=None)
  error_code: str = Field(
    description="에러 코드"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "success": False,
        "message": "요청 처리 중 오류가 발생했습니다.",
        "data": None,
        "error_code": "INTERNAL_SERVER_ERROR",
        "details": {}
      }
    }


class PaginationMeta(BaseModel):
  """
  페이지네이션 메타데이터

  목록 조회 응답에 포함되는 페이지네이션 정보입니다.
  """

  total: int = Field(
    description="전체 항목 수"
  )
  page: int = Field(
    description="현재 페이지 번호 (1부터 시작)"
  )
  page_size: int = Field(
    description="페이지당 항목 수"
  )
  total_pages: int = Field(
    description="전체 페이지 수"
  )
  has_next: bool = Field(
    description="다음 페이지 존재 여부"
  )
  has_prev: bool = Field(
    description="이전 페이지 존재 여부"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5,
        "has_next": True,
        "has_prev": False
      }
    }


class PaginatedResponse(BaseResponse[T], Generic[T]):
  """
  페이지네이션 응답 스키마

  목록 조회 시 페이지네이션 정보를 포함하는 응답입니다.
  """

  success: bool = Field(default=True)
  meta: PaginationMeta = Field(
    description="페이지네이션 메타데이터"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "success": True,
        "message": "조회 성공",
        "data": [],
        "meta": {
          "total": 100,
          "page": 1,
          "page_size": 20,
          "total_pages": 5,
          "has_next": True,
          "has_prev": False
        },
        "error_code": None,
        "details": None
      }
    }


class HealthCheckResponse(BaseModel):
  """
  헬스체크 응답 스키마
  """

  status: str = Field(
    description="서비스 상태"
  )
  database: str = Field(
    description="데이터베이스 연결 상태"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "status": "healthy",
        "database": "connected"
      }
    }
