"""
Alembic 마이그레이션 환경 설정

SQLAlchemy 모델을 자동으로 감지하고 마이그레이션을 생성합니다.
"""
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# app 모듈 import
from app.core.config import settings
from app.models.base import Base

# User 모델을 명시적으로 import (자동 감지를 위해 필요)
from app.models.user import User  # noqa: F401

# Alembic Config 객체 (alembic.ini 값 접근)
config = context.config

# 환경변수에서 DATABASE_URL 가져오기
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Logging 설정 (alembic.ini의 loggers 섹션 사용)
if config.config_file_name is not None:
  fileConfig(config.config_file_name)

# 자동 마이그레이션 생성을 위한 메타데이터
target_metadata = Base.metadata


def run_migrations_offline() -> None:
  """
  오프라인 모드에서 마이그레이션 실행

  실제 데이터베이스 연결 없이 SQL 스크립트만 생성합니다.
  """
  url = config.get_main_option("sqlalchemy.url")
  context.configure(
    url=url,
    target_metadata=target_metadata,
    literal_binds=True,
    dialect_opts={"paramstyle": "named"},
  )

  with context.begin_transaction():
    context.run_migrations()


def run_migrations_online() -> None:
  """
  온라인 모드에서 마이그레이션 실행

  데이터베이스에 실제로 연결하여 마이그레이션을 적용합니다.
  """
  connectable = engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
  )

  with connectable.connect() as connection:
    context.configure(
      connection=connection,
      target_metadata=target_metadata
    )

    with context.begin_transaction():
      context.run_migrations()


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
