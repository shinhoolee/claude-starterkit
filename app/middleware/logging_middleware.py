"""
로깅 미들웨어

모든 HTTP 요청/응답을 로깅하고 처리 시간을 측정합니다.
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
  """
  HTTP 요청/응답 로깅 미들웨어

  각 요청에 대해 다음 정보를 로깅합니다:
  - HTTP 메서드 및 경로
  - 클라이언트 IP
  - User-Agent
  - 처리 시간
  - 응답 상태 코드
  """

  async def dispatch(self, request: Request, call_next: Callable) -> Response:
    """
    요청 전후로 로깅을 수행합니다.
    """
    # 요청 시작 시간 기록
    start_time = time.time()

    # 클라이언트 정보 추출
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # 요청 정보 로깅
    logger.info(
      f"요청 시작: {request.method} {request.url.path}",
      extra={
        "method": request.method,
        "path": request.url.path,
        "query_params": str(request.query_params),
        "client_ip": client_host,
        "user_agent": user_agent
      }
    )

    # 응답 처리
    try:
      response = await call_next(request)
    except Exception as e:
      # 예외 발생 시 로깅 (예외는 전역 핸들러에서 처리됨)
      process_time = time.time() - start_time
      logger.error(
        f"요청 처리 중 예외 발생: {request.method} {request.url.path}",
        extra={
          "method": request.method,
          "path": request.url.path,
          "client_ip": client_host,
          "process_time": f"{process_time:.3f}s",
          "error": str(e)
        },
        exc_info=True
      )
      raise

    # 처리 시간 계산
    process_time = time.time() - start_time

    # 응답에 처리 시간 헤더 추가
    response.headers["X-Process-Time"] = f"{process_time:.3f}"

    # 응답 정보 로깅 (상태 코드에 따라 로그 레벨 결정)
    log_level = logging.INFO
    if response.status_code >= 500:
      log_level = logging.ERROR
    elif response.status_code >= 400:
      log_level = logging.WARNING

    logger.log(
      log_level,
      f"요청 완료: {request.method} {request.url.path} - {response.status_code}",
      extra={
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "client_ip": client_host,
        "process_time": f"{process_time:.3f}s"
      }
    )

    return response
