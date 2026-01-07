"""
Pytest 설정 및 공통 Fixture

테스트용 데이터베이스, 클라이언트, 인증 사용자 등의 Fixture를 제공합니다.
"""
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.user import User
from app.core.security import hash_password, create_access_token


# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
  SQLALCHEMY_TEST_DATABASE_URL,
  connect_args={"check_same_thread": False},
  poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
  autocommit=False,
  autoflush=False,
  bind=engine
)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
  """
  테스트용 데이터베이스 세션 Fixture

  각 테스트마다 새로운 테이블을 생성하고 테스트 후 삭제합니다.
  """
  # 테이블 생성
  Base.metadata.create_all(bind=engine)

  db = TestingSessionLocal()
  try:
    yield db
  finally:
    db.close()
    # 테이블 삭제
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
  """
  테스트용 FastAPI 클라이언트 Fixture

  테스트용 DB 세션을 주입한 클라이언트를 반환합니다.
  """
  def override_get_db():
    try:
      yield db
    finally:
      pass

  app.dependency_overrides[get_db] = override_get_db
  with TestClient(app) as test_client:
    yield test_client
  app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
  """
  테스트용 일반 사용자 Fixture

  Returns:
    User: 테스트용 사용자 객체
  """
  user = User(
    email="test@example.com",
    username="testuser",
    hashed_password=hash_password("testpassword123"),
    full_name="Test User",
    is_active=True,
    is_superuser=False
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


@pytest.fixture
def test_superuser(db: Session) -> User:
  """
  테스트용 관리자 사용자 Fixture

  Returns:
    User: 테스트용 관리자 객체
  """
  user = User(
    email="admin@example.com",
    username="adminuser",
    hashed_password=hash_password("adminpassword123"),
    full_name="Admin User",
    is_active=True,
    is_superuser=True
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
  """
  테스트용 일반 사용자 JWT 토큰 Fixture

  Returns:
    str: Access Token
  """
  return create_access_token(subject=test_user.email)


@pytest.fixture
def test_superuser_token(test_superuser: User) -> str:
  """
  테스트용 관리자 JWT 토큰 Fixture

  Returns:
    str: Access Token
  """
  return create_access_token(subject=test_superuser.email)


@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
  """
  테스트용 일반 사용자 인증 헤더 Fixture

  test_user fixture에 직접 의존하여 동일한 DB 세션을 공유합니다.

  Returns:
    Dict[str, str]: Authorization 헤더
  """
  token = create_access_token(subject=test_user.email)
  return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_superuser: User) -> Dict[str, str]:
  """
  테스트용 관리자 인증 헤더 Fixture

  test_superuser fixture에 직접 의존하여 동일한 DB 세션을 공유합니다.

  Returns:
    Dict[str, str]: Authorization 헤더
  """
  token = create_access_token(subject=test_superuser.email)
  return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_create_data() -> Dict[str, Any]:
  """
  테스트용 사용자 생성 데이터 Fixture

  Returns:
    Dict[str, Any]: 사용자 생성 요청 데이터
  """
  return {
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "newpassword123",
    "full_name": "New User"
  }


@pytest.fixture
def user_login_data() -> Dict[str, str]:
  """
  테스트용 로그인 데이터 Fixture

  Returns:
    Dict[str, str]: 로그인 요청 데이터
  """
  return {
    "email": "test@example.com",
    "password": "testpassword123"
  }
