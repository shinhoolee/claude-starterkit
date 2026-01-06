"""
커스텀 예외 클래스 정의

계층적 예외 구조를 통해 일관된 에러 처리를 제공합니다.
모든 커스텀 예외는 BaseAPIException을 상속받습니다.
"""
from typing import Any, Optional, Dict


class BaseAPIException(Exception):
  """
  기본 API 예외 클래스

  모든 커스텀 예외의 부모 클래스입니다.
  HTTP 상태 코드, 에러 메시지, 에러 코드, 추가 세부정보를 포함할 수 있습니다.
  """

  def __init__(
    self,
    message: str,
    status_code: int = 500,
    error_code: str = "INTERNAL_SERVER_ERROR",
    details: Optional[Dict[str, Any]] = None
  ):
    self.message = message
    self.status_code = status_code
    self.error_code = error_code
    self.details = details or {}
    super().__init__(self.message)


class EntityNotFoundException(BaseAPIException):
  """
  엔티티를 찾을 수 없을 때 발생하는 예외 (404)

  예시:
    - 존재하지 않는 사용자 ID로 조회 시도
    - 삭제된 리소스 접근 시도
  """

  def __init__(
    self,
    message: str = "요청한 리소스를 찾을 수 없습니다.",
    details: Optional[Dict[str, Any]] = None
  ):
    super().__init__(
      message=message,
      status_code=404,
      error_code="ENTITY_NOT_FOUND",
      details=details
    )


class DuplicateEntityException(BaseAPIException):
  """
  중복된 엔티티가 존재할 때 발생하는 예외 (409)

  예시:
    - 이미 존재하는 이메일로 회원가입 시도
    - 고유 제약조건 위반
  """

  def __init__(
    self,
    message: str = "이미 존재하는 리소스입니다.",
    details: Optional[Dict[str, Any]] = None
  ):
    super().__init__(
      message=message,
      status_code=409,
      error_code="DUPLICATE_ENTITY",
      details=details
    )


class UnauthorizedException(BaseAPIException):
  """
  인증되지 않은 사용자 접근 시 발생하는 예외 (401)

  예시:
    - JWT 토큰 없이 인증 필요 API 호출
    - 만료된 토큰으로 요청
    - 잘못된 토큰 형식
  """

  def __init__(
    self,
    message: str = "인증이 필요합니다.",
    details: Optional[Dict[str, Any]] = None
  ):
    super().__init__(
      message=message,
      status_code=401,
      error_code="UNAUTHORIZED",
      details=details
    )


class ForbiddenException(BaseAPIException):
  """
  권한이 없는 사용자 접근 시 발생하는 예외 (403)

  예시:
    - 일반 사용자가 관리자 전용 API 호출
    - 다른 사용자의 리소스 수정 시도
  """

  def __init__(
    self,
    message: str = "해당 리소스에 접근할 권한이 없습니다.",
    details: Optional[Dict[str, Any]] = None
  ):
    super().__init__(
      message=message,
      status_code=403,
      error_code="FORBIDDEN",
      details=details
    )


class ValidationException(BaseAPIException):
  """
  비즈니스 로직 유효성 검증 실패 시 발생하는 예외 (422)

  Pydantic 유효성 검증과 구분되는 비즈니스 규칙 위반 시 사용합니다.

  예시:
    - 비밀번호 정책 위반 (너무 약함)
    - 비즈니스 규칙 위반 (최대 수량 초과 등)
  """

  def __init__(
    self,
    message: str = "유효성 검증에 실패했습니다.",
    details: Optional[Dict[str, Any]] = None
  ):
    super().__init__(
      message=message,
      status_code=422,
      error_code="VALIDATION_ERROR",
      details=details
    )


class DatabaseException(BaseAPIException):
  """
  데이터베이스 작업 실패 시 발생하는 예외 (500)

  예시:
    - DB 연결 실패
    - 트랜잭션 롤백
    - 쿼리 실행 오류
  """

  def __init__(
    self,
    message: str = "데이터베이스 작업 중 오류가 발생했습니다.",
    details: Optional[Dict[str, Any]] = None
  ):
    super().__init__(
      message=message,
      status_code=500,
      error_code="DATABASE_ERROR",
      details=details
    )


class BadRequestException(BaseAPIException):
  """
  잘못된 요청 시 발생하는 예외 (400)

  예시:
    - 필수 파라미터 누락
    - 잘못된 요청 포맷
  """

  def __init__(
    self,
    message: str = "잘못된 요청입니다.",
    details: Optional[Dict[str, Any]] = None
  ):
    super().__init__(
      message=message,
      status_code=400,
      error_code="BAD_REQUEST",
      details=details
    )
