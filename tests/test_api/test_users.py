"""
Users API 테스트

사용자 관련 API 엔드포인트 테스트를 수행합니다.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestCreateUser:
  """회원가입 API 테스트"""

  def test_create_user_success(
    self,
    client: TestClient,
    user_create_data: dict
  ):
    """정상 회원가입 테스트"""
    response = client.post("/api/v1/users", json=user_create_data)

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == user_create_data["email"]
    assert data["data"]["username"] == user_create_data["username"]
    assert "hashed_password" not in data["data"]

  def test_create_user_duplicate_email(
    self,
    client: TestClient,
    test_user: User,
    user_create_data: dict
  ):
    """중복 이메일로 회원가입 시도"""
    user_create_data["email"] = test_user.email
    response = client.post("/api/v1/users", json=user_create_data)

    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert "DUPLICATE" in data.get("error_code", "")

  def test_create_user_duplicate_username(
    self,
    client: TestClient,
    test_user: User,
    user_create_data: dict
  ):
    """중복 사용자명으로 회원가입 시도"""
    user_create_data["username"] = test_user.username
    response = client.post("/api/v1/users", json=user_create_data)

    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False

  def test_create_user_invalid_email(
    self,
    client: TestClient,
    user_create_data: dict
  ):
    """잘못된 이메일 형식으로 회원가입 시도"""
    user_create_data["email"] = "invalid-email"
    response = client.post("/api/v1/users", json=user_create_data)

    assert response.status_code == 422

  def test_create_user_short_password(
    self,
    client: TestClient,
    user_create_data: dict
  ):
    """짧은 비밀번호로 회원가입 시도"""
    user_create_data["password"] = "short"
    response = client.post("/api/v1/users", json=user_create_data)

    assert response.status_code == 422


class TestGetUsers:
  """사용자 목록 조회 API 테스트"""

  def test_get_users_success(
    self,
    client: TestClient,
    test_user: User,
    auth_headers: dict
  ):
    """인증된 사용자의 목록 조회 성공"""
    response = client.get("/api/v1/users", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert "meta" in data
    assert data["meta"]["total"] >= 1

  def test_get_users_without_auth(
    self,
    client: TestClient
  ):
    """인증 없이 목록 조회 시도"""
    response = client.get("/api/v1/users")

    assert response.status_code == 401

  def test_get_users_pagination(
    self,
    client: TestClient,
    db: Session,
    test_user: User,
    auth_headers: dict
  ):
    """페이지네이션 테스트"""
    # 추가 사용자 생성
    from app.core.security import hash_password
    for i in range(5):
      user = User(
        email=f"user{i}@example.com",
        username=f"user{i}",
        hashed_password=hash_password("password123"),
        is_active=True
      )
      db.add(user)
    db.commit()

    # 첫 페이지 조회
    response = client.get(
      "/api/v1/users?page=1&page_size=3",
      headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["meta"]["page"] == 1
    assert data["meta"]["page_size"] == 3
    assert data["meta"]["has_next"] is True


class TestGetUser:
  """사용자 조회 API 테스트"""

  def test_get_user_success(
    self,
    client: TestClient,
    test_user: User,
    auth_headers: dict
  ):
    """특정 사용자 조회 성공"""
    response = client.get(
      f"/api/v1/users/{test_user.id}",
      headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == test_user.id
    assert data["data"]["email"] == test_user.email

  def test_get_user_not_found(
    self,
    client: TestClient,
    test_user: User,
    auth_headers: dict
  ):
    """존재하지 않는 사용자 조회"""
    response = client.get("/api/v1/users/99999", headers=auth_headers)

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "NOT_FOUND" in data.get("error_code", "")


class TestUpdateUser:
  """사용자 수정 API 테스트"""

  def test_update_user_self(
    self,
    client: TestClient,
    test_user: User,
    auth_headers: dict
  ):
    """본인 정보 수정 성공"""
    response = client.put(
      f"/api/v1/users/{test_user.id}",
      headers=auth_headers,
      json={"full_name": "Updated Name"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["full_name"] == "Updated Name"

  def test_update_user_others_forbidden(
    self,
    client: TestClient,
    test_user: User,
    test_superuser: User,
    auth_headers: dict
  ):
    """다른 사용자 정보 수정 시도 (일반 사용자)"""
    response = client.put(
      f"/api/v1/users/{test_superuser.id}",
      headers=auth_headers,
      json={"full_name": "Hacked Name"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert "FORBIDDEN" in data.get("error_code", "")

  def test_update_user_by_admin(
    self,
    client: TestClient,
    test_user: User,
    admin_auth_headers: dict
  ):
    """관리자가 다른 사용자 정보 수정"""
    response = client.put(
      f"/api/v1/users/{test_user.id}",
      headers=admin_auth_headers,
      json={"full_name": "Admin Updated"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["full_name"] == "Admin Updated"


class TestDeleteUser:
  """사용자 삭제 API 테스트"""

  def test_delete_user_by_admin(
    self,
    client: TestClient,
    test_user: User,
    admin_auth_headers: dict
  ):
    """관리자가 사용자 삭제 성공"""
    response = client.delete(
      f"/api/v1/users/{test_user.id}",
      headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # 삭제 확인
    get_response = client.get(
      f"/api/v1/users/{test_user.id}",
      headers=admin_auth_headers
    )
    assert get_response.status_code == 404

  def test_delete_user_by_normal_user(
    self,
    client: TestClient,
    test_superuser: User,
    auth_headers: dict
  ):
    """일반 사용자가 삭제 시도"""
    response = client.delete(
      f"/api/v1/users/{test_superuser.id}",
      headers=auth_headers
    )

    assert response.status_code == 403

  def test_delete_user_not_found(
    self,
    client: TestClient,
    admin_auth_headers: dict
  ):
    """존재하지 않는 사용자 삭제 시도"""
    response = client.delete(
      "/api/v1/users/99999",
      headers=admin_auth_headers
    )

    assert response.status_code == 404
