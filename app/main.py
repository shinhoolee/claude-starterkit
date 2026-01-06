"""
FastAPI 애플리케이션 진입점

애플리케이션을 초기화하고 미들웨어, CORS, 라우터, 예외 핸들러를 등록합니다.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging_middleware import LoggingMiddleware
from app.api.v1.router import api_router

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
  title="FastAPI Starter Kit",
  description="FastAPI 기반의 재사용 가능한 백엔드 API Starter Kit",
  version="1.0.0",
  docs_url="/docs",
  redoc_url="/redoc",
  openapi_url="/openapi.json"
)

# CORS 미들웨어 설정
app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.get_cors_origins(),
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# 로깅 미들웨어 등록
app.add_middleware(LoggingMiddleware)

# 전역 예외 핸들러 등록
register_exception_handlers(app)

# API 라우터 등록
app.include_router(
  api_router,
  prefix="/api/v1"
)


@app.on_event("startup")
async def startup_event():
  """
  애플리케이션 시작 시 실행되는 이벤트

  데이터베이스 연결 테스트 등을 수행합니다.
  """
  logger.info("=" * 60)
  logger.info("FastAPI 애플리케이션 시작")
  logger.info(f"환경: {settings.ENV}")
  logger.info(f"디버그 모드: {settings.DEBUG}")
  logger.info("=" * 60)

  # 데이터베이스 연결 테스트
  from app.core.database import test_db_connection
  if test_db_connection():
    logger.info("✅ 데이터베이스 연결 성공")
  else:
    logger.error("❌ 데이터베이스 연결 실패")


@app.on_event("shutdown")
async def shutdown_event():
  """
  애플리케이션 종료 시 실행되는 이벤트
  """
  logger.info("=" * 60)
  logger.info("FastAPI 애플리케이션 종료")
  logger.info("=" * 60)


@app.get("/")
async def root():
  """
  루트 엔드포인트

  API 기본 정보를 반환합니다.
  """
  return {
    "message": "FastAPI Starter Kit API",
    "version": "1.0.0",
    "docs": "/docs",
    "health": "/api/v1/health"
  }
