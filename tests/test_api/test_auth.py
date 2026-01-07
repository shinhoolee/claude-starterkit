"""
Auth API 테스트

인증 관련 API 엔드포인트 테스트를 수행합니다.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestLogin:
  """로그인 API 테스트"""

  def test_login_success(
    self,
    client: TestClient,
    test_user: User,
    user_login_data: dict
  ):
    """정상 로그인 테스트"""
    response = client.post("/api/v1/auth/login", json=user_login_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"

  def test_login_wrong_email(
    self,
    client: TestClient,
    test_user: User
  ):
    """잘못된 이메일로 로그인 시도"""
    response = client.post("/api/v1/auth/login", json={
      "email": "wrong@example.com",
      "password": "testpassword123"
    })

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "UNAUTHORIZED" in data.get("error_code", "")

  def test_login_wrong_password(
    self,
    client: TestClient,
    test_user: User,
    user_login_data: dict
  ):
    """잘못된 비밀번호로 로그인 시도"""
    user_login_data["password"] = "wrongpassword"
    response = client.post("/api/v1/auth/login", json=user_login_data)

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False

  def test_login_inactive_user(
    self,
    client: TestClient,
    db: Session,
    test_user: User,
    user_login_data: dict
  ):
    """비활성화된 사용자 로그인 시도"""
    # 사용자 비활성화
    test_user.is_active = False
    db.commit()

    response = client.post("/api/v1/auth/login", json=user_login_data)

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


class TestRefreshToken:
  """토큰 갱신 API 테스트"""

  def test_refresh_token_success(
    self,
    client: TestClient,
    test_user: User,
    user_login_data: dict
  ):
    """정상 토큰 갱신 테스트"""
    # 먼저 로그인하여 refresh_token 획득
    login_response = client.post("/api/v1/auth/login", json=user_login_data)
    refresh_token = login_response.json()["data"]["refresh_token"]

    # 토큰 갱신
    response = client.post("/api/v1/auth/refresh", json={
      "refresh_token": refresh_token
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"

  def test_refresh_token_invalid(
    self,
    client: TestClient,
    test_user: User
  ):
    """잘못된 refresh_token으로 갱신 시도"""
    response = client.post("/api/v1/auth/refresh", json={
      "refresh_token": "invalid_token"
    })

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


class TestGetCurrentUser:
  """현재 사용자 정보 조회 API 테스트"""

  def test_get_me_success(
    self,
    client: TestClient,
    test_user: User,
    auth_headers: dict
  ):
    """인증된 사용자 정보 조회 성공"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user.email
    assert data["data"]["username"] == test_user.username

  def test_get_me_without_token(
    self,
    client: TestClient
  ):
    """토큰 없이 사용자 정보 조회 시도"""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401

  def test_get_me_invalid_token(
    self,
    client: TestClient
  ):
    """잘못된 토큰으로 사용자 정보 조회 시도"""
    response = client.get("/api/v1/auth/me", headers={
      "Authorization": "Bearer invalid_token"
    })

    assert response.status_code == 401
