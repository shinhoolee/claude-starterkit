"""
응답 헬퍼 유틸리티

표준 응답 객체를 생성하는 헬퍼 함수들을 제공합니다.
"""
from typing import TypeVar, Optional, Any, Dict, List
from math import ceil

from app.schemas.common import (
  SuccessResponse,
  ErrorResponse,
  PaginatedResponse,
  PaginationMeta
)

T = TypeVar("T")


def success_response(
  data: T,
  message: str = "요청이 성공적으로 처리되었습니다."
) -> SuccessResponse[T]:
  """
  성공 응답 생성

  Args:
    data: 응답 데이터
    message: 응답 메시지

  Returns:
    SuccessResponse: 표준 성공 응답 객체

  Example:
    >>> user = {"id": 1, "name": "홍길동"}
    >>> return success_response(user, "사용자 조회 성공")
  """
  return SuccessResponse(
    success=True,
    message=message,
    data=data
  )


def error_response(
  message: str,
  error_code: str = "INTERNAL_SERVER_ERROR",
  details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
  """
  에러 응답 생성

  Args:
    message: 에러 메시지
    error_code: 에러 코드
    details: 추가 세부 정보

  Returns:
    ErrorResponse: 표준 에러 응답 객체

  Example:
    >>> return error_response(
    ...   message="사용자를 찾을 수 없습니다.",
    ...   error_code="USER_NOT_FOUND"
    ... )
  """
  return ErrorResponse(
    success=False,
    message=message,
    error_code=error_code,
    details=details or {}
  )


def paginated_response(
  data: List[T],
  total: int,
  page: int,
  page_size: int,
  message: str = "조회 성공"
) -> PaginatedResponse[List[T]]:
  """
  페이지네이션 응답 생성

  Args:
    data: 현재 페이지 데이터 목록
    total: 전체 항목 수
    page: 현재 페이지 번호 (1부터 시작)
    page_size: 페이지당 항목 수
    message: 응답 메시지

  Returns:
    PaginatedResponse: 페이지네이션 정보가 포함된 응답 객체

  Example:
    >>> users = [{"id": 1, "name": "홍길동"}, {"id": 2, "name": "김철수"}]
    >>> return paginated_response(
    ...   data=users,
    ...   total=100,
    ...   page=1,
    ...   page_size=20
    ... )
  """
  # 전체 페이지 수 계산
  total_pages = ceil(total / page_size) if page_size > 0 else 0

  # 페이지네이션 메타데이터 생성
  meta = PaginationMeta(
    total=total,
    page=page,
    page_size=page_size,
    total_pages=total_pages,
    has_next=page < total_pages,
    has_prev=page > 1
  )

  return PaginatedResponse(
    success=True,
    message=message,
    data=data,
    meta=meta
  )


def created_response(
  data: T,
  message: str = "리소스가 성공적으로 생성되었습니다."
) -> SuccessResponse[T]:
  """
  생성 성공 응답 (201 Created용)

  Args:
    data: 생성된 리소스 데이터
    message: 응답 메시지

  Returns:
    SuccessResponse: 표준 성공 응답 객체

  Example:
    >>> new_user = {"id": 1, "name": "홍길동"}
    >>> return created_response(new_user, "사용자 생성 성공")
  """
  return success_response(data=data, message=message)


def no_content_response(
  message: str = "요청이 성공적으로 처리되었습니다."
) -> SuccessResponse[None]:
  """
  내용 없음 응답 (204 No Content용)

  Args:
    message: 응답 메시지

  Returns:
    SuccessResponse: 데이터가 None인 성공 응답 객체

  Example:
    >>> return no_content_response("사용자가 삭제되었습니다.")
  """
  return SuccessResponse(
    success=True,
    message=message,
    data=None
  )
