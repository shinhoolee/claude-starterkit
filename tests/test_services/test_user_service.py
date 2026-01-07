"""
User Service 테스트

UserService 비즈니스 로직 테스트를 수행합니다.
"""
import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import user_service
from app.core.exceptions import (
  EntityNotFoundException,
  DuplicateEntityException
)


class TestCreateUser:
  """사용자 생성 서비스 테스트"""

  def test_create_user_success(self, db: Session):
    """정상 사용자 생성"""
    user_in = UserCreate(
      email="service_test@example.com",
      username="service_test_user",
      password="testpassword123",
      full_name="Service Test User"
    )

    user = user_service.create_user(db, user_in)

    assert user.id is not None
    assert user.email == user_in.email
    assert user.username == user_in.username
    assert user.full_name == user_in.full_name
    assert user.is_active is True
    assert user.is_superuser is False
    # 비밀번호가 해시되었는지 확인
    assert user.hashed_password != user_in.password

  def test_create_user_duplicate_email(
    self,
    db: Session,
    test_user: User
  ):
    """중복 이메일로 사용자 생성 시도"""
    user_in = UserCreate(
      email=test_user.email,  # 중복 이메일
      username="new_username",
      password="testpassword123"
    )

    with pytest.raises(DuplicateEntityException) as exc_info:
      user_service.create_user(db, user_in)

    assert "이메일" in str(exc_info.value.message)

  def test_create_user_duplicate_username(
    self,
    db: Session,
    test_user: User
  ):
    """중복 사용자명으로 사용자 생성 시도"""
    user_in = UserCreate(
      email="unique@example.com",
      username=test_user.username,  # 중복 사용자명
      password="testpassword123"
    )

    with pytest.raises(DuplicateEntityException) as exc_info:
      user_service.create_user(db, user_in)

    assert "사용자명" in str(exc_info.value.message)


class TestGetUser:
  """사용자 조회 서비스 테스트"""

  def test_get_user_success(
    self,
    db: Session,
    test_user: User
  ):
    """정상 사용자 조회"""
    user = user_service.get_user(db, test_user.id)

    assert user.id == test_user.id
    assert user.email == test_user.email

  def test_get_user_not_found(self, db: Session):
    """존재하지 않는 사용자 조회"""
    with pytest.raises(EntityNotFoundException) as exc_info:
      user_service.get_user(db, 99999)

    assert "찾을 수 없습니다" in str(exc_info.value.message)

  def test_get_user_by_email(
    self,
    db: Session,
    test_user: User
  ):
    """이메일로 사용자 조회"""
    user = user_service.get_user_by_email(db, test_user.email)

    assert user is not None
    assert user.id == test_user.id

  def test_get_user_by_email_not_found(self, db: Session):
    """존재하지 않는 이메일로 조회"""
    user = user_service.get_user_by_email(db, "notfound@example.com")

    assert user is None


class TestGetUsers:
  """사용자 목록 조회 서비스 테스트"""

  def test_get_users(
    self,
    db: Session,
    test_user: User
  ):
    """사용자 목록 조회"""
    users = user_service.get_users(db)

    assert isinstance(users, list)
    assert len(users) >= 1
    assert any(u.id == test_user.id for u in users)

  def test_get_users_with_pagination(
    self,
    db: Session,
    test_user: User
  ):
    """페이지네이션을 적용한 사용자 목록 조회"""
    # 추가 사용자 생성
    from app.core.security import hash_password
    for i in range(5):
      user = User(
        email=f"pagination{i}@example.com",
        username=f"pagination{i}",
        hashed_password=hash_password("password"),
        is_active=True
      )
      db.add(user)
    db.commit()

    # 첫 페이지
    users = user_service.get_users(db, skip=0, limit=3)
    assert len(users) == 3

    # 두 번째 페이지
    users = user_service.get_users(db, skip=3, limit=3)
    assert len(users) == 3

  def test_get_users_count(
    self,
    db: Session,
    test_user: User
  ):
    """사용자 수 조회"""
    count = user_service.get_users_count(db)

    assert count >= 1


class TestUpdateUser:
  """사용자 수정 서비스 테스트"""

  def test_update_user_full_name(
    self,
    db: Session,
    test_user: User
  ):
    """사용자 이름 수정"""
    user_in = UserUpdate(full_name="Updated Full Name")

    updated_user = user_service.update_user(db, test_user.id, user_in)

    assert updated_user.full_name == "Updated Full Name"

  def test_update_user_username(
    self,
    db: Session,
    test_user: User
  ):
    """사용자명 수정"""
    user_in = UserUpdate(username="updated_username")

    updated_user = user_service.update_user(db, test_user.id, user_in)

    assert updated_user.username == "updated_username"

  def test_update_user_duplicate_username(
    self,
    db: Session,
    test_user: User,
    test_superuser: User
  ):
    """중복 사용자명으로 수정 시도"""
    user_in = UserUpdate(username=test_superuser.username)

    with pytest.raises(DuplicateEntityException):
      user_service.update_user(db, test_user.id, user_in)

  def test_update_user_password(
    self,
    db: Session,
    test_user: User
  ):
    """비밀번호 수정"""
    old_password_hash = test_user.hashed_password
    user_in = UserUpdate(password="newpassword123")

    updated_user = user_service.update_user(db, test_user.id, user_in)

    assert updated_user.hashed_password != old_password_hash
    assert updated_user.hashed_password != "newpassword123"

  def test_update_user_not_found(self, db: Session):
    """존재하지 않는 사용자 수정 시도"""
    user_in = UserUpdate(full_name="Test")

    with pytest.raises(EntityNotFoundException):
      user_service.update_user(db, 99999, user_in)


class TestDeleteUser:
  """사용자 삭제 서비스 테스트"""

  def test_delete_user_success(
    self,
    db: Session,
    test_user: User
  ):
    """정상 사용자 삭제"""
    user_id = test_user.id
    deleted_user = user_service.delete_user(db, user_id)

    assert deleted_user.id == user_id

    # 삭제 확인
    with pytest.raises(EntityNotFoundException):
      user_service.get_user(db, user_id)

  def test_delete_user_not_found(self, db: Session):
    """존재하지 않는 사용자 삭제 시도"""
    with pytest.raises(EntityNotFoundException):
      user_service.delete_user(db, 99999)


class TestDeactivateUser:
  """사용자 비활성화 서비스 테스트"""

  def test_deactivate_user_success(
    self,
    db: Session,
    test_user: User
  ):
    """사용자 비활성화 성공"""
    assert test_user.is_active is True

    deactivated_user = user_service.deactivate_user(db, test_user.id)

    assert deactivated_user.is_active is False

  def test_deactivate_user_not_found(self, db: Session):
    """존재하지 않는 사용자 비활성화 시도"""
    with pytest.raises(EntityNotFoundException):
      user_service.deactivate_user(db, 99999)
