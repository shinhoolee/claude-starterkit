"""
환경변수 관리 및 애플리케이션 설정

pydantic-settings를 사용하여 환경변수를 타입 안전하게 로드하고 검증합니다.
"""
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """애플리케이션 설정 클래스"""

  # 애플리케이션 기본 설정
  ENV: str = "development"
  DEBUG: bool = True
  SECRET_KEY: str

  # 데이터베이스 설정
  DATABASE_URL: str

  # JWT 설정
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
  REFRESH_TOKEN_EXPIRE_DAYS: int = 7

  # CORS 설정
  CORS_ORIGINS: str = "http://localhost:3000"

  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True
  )

  @field_validator("SECRET_KEY")
  @classmethod
  def validate_secret_key(cls, v: str) -> str:
    """SECRET_KEY 최소 길이 검증 (32자 이상)"""
    if len(v) < 32:
      raise ValueError("SECRET_KEY는 최소 32자 이상이어야 합니다.")
    return v

  def get_cors_origins(self) -> List[str]:
    """CORS_ORIGINS 문자열을 리스트로 변환"""
    return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# 전역 설정 인스턴스 (Singleton 패턴)
settings = Settings()
