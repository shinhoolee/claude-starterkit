"""
애플리케이션 로깅 설정

Python 표준 logging 모듈을 사용하여 구조화된 로깅 시스템을 제공합니다.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:
  """로깅 시스템 초기화"""

  # 로그 디렉토리 생성
  log_dir = Path("logs")
  log_dir.mkdir(exist_ok=True)

  # 로그 포맷 설정
  log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format = "%Y-%m-%d %H:%M:%S"

  formatter = logging.Formatter(log_format, datefmt=date_format)

  # 루트 로거 설정
  root_logger = logging.getLogger()
  root_logger.setLevel(logging.INFO)

  # 기존 핸들러 제거 (중복 방지)
  root_logger.handlers.clear()

  # 1. 콘솔 핸들러 (개발 환경용)
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setLevel(logging.INFO)
  console_handler.setFormatter(formatter)
  root_logger.addHandler(console_handler)

  # 2. 파일 핸들러 - 전체 로그 (app.log, 10MB 로테이션)
  file_handler = RotatingFileHandler(
    log_dir / "app.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding="utf-8"
  )
  file_handler.setLevel(logging.INFO)
  file_handler.setFormatter(formatter)
  root_logger.addHandler(file_handler)

  # 3. 파일 핸들러 - 에러 로그만 (error.log, 10MB 로테이션)
  error_handler = RotatingFileHandler(
    log_dir / "error.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding="utf-8"
  )
  error_handler.setLevel(logging.ERROR)
  error_handler.setFormatter(formatter)
  root_logger.addHandler(error_handler)

  # 외부 라이브러리 로그 레벨 조정 (노이즈 감소)
  logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
  logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

  logging.info("로깅 시스템 초기화 완료")


def get_logger(name: str) -> logging.Logger:
  """모듈별 로거 생성"""
  return logging.getLogger(name)
