"""
User DTO (Data Transfer Object)

사용자 관련 요청/응답 스키마를 정의합니다.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
  """사용자 기본 스키마"""

  email: EmailStr = Field(
    description="이메일 주소"
  )
  username: str = Field(
    min_length=3,
    max_length=50,
    description="사용자명 (3-50자)"
  )
  full_name: Optional[str] = Field(
    default=None,
    max_length=100,
    description="전체 이름"
  )


class UserCreate(UserBase):
  """
  사용자 생성 요청 스키마

  회원가입 시 사용됩니다.
  """

  password: str = Field(
    min_length=8,
    max_length=100,
    description="비밀번호 (8자 이상)"
  )

  @field_validator("password")
  @classmethod
  def validate_password(cls, v: str) -> str:
    """비밀번호 복잡도 검증"""
    if not any(char.isdigit() for char in v):
      raise ValueError("비밀번호는 최소 1개 이상의 숫자를 포함해야 합니다.")
    if not any(char.isalpha() for char in v):
      raise ValueError("비밀번호는 최소 1개 이상의 영문자를 포함해야 합니다.")
    return v

  class Config:
    json_schema_extra = {
      "example": {
        "email": "user@example.com",
        "username": "johndoe",
        "full_name": "홍길동",
        "password": "securepass123"
      }
    }


class UserUpdate(BaseModel):
  """
  사용자 수정 요청 스키마

  모든 필드가 선택사항입니다.
  """

  username: Optional[str] = Field(
    default=None,
    min_length=3,
    max_length=50,
    description="사용자명 (3-50자)"
  )
  full_name: Optional[str] = Field(
    default=None,
    max_length=100,
    description="전체 이름"
  )
  password: Optional[str] = Field(
    default=None,
    min_length=8,
    max_length=100,
    description="새 비밀번호 (8자 이상)"
  )
  is_active: Optional[bool] = Field(
    default=None,
    description="계정 활성화 상태"
  )

  @field_validator("password")
  @classmethod
  def validate_password(cls, v: Optional[str]) -> Optional[str]:
    """비밀번호 복잡도 검증"""
    if v is None:
      return v
    if not any(char.isdigit() for char in v):
      raise ValueError("비밀번호는 최소 1개 이상의 숫자를 포함해야 합니다.")
    if not any(char.isalpha() for char in v):
      raise ValueError("비밀번호는 최소 1개 이상의 영문자를 포함해야 합니다.")
    return v

  class Config:
    json_schema_extra = {
      "example": {
        "username": "johndoe_updated",
        "full_name": "홍길동",
        "password": "newsecurepass123"
      }
    }


class UserResponse(UserBase):
  """
  사용자 응답 스키마

  비밀번호를 제외한 사용자 정보를 반환합니다.
  """

  id: int = Field(
    description="사용자 고유 ID"
  )
  is_active: bool = Field(
    description="계정 활성화 상태"
  )
  is_superuser: bool = Field(
    description="관리자 여부"
  )
  created_at: datetime = Field(
    description="생성 일시"
  )
  updated_at: datetime = Field(
    description="수정 일시"
  )

  class Config:
    from_attributes = True
    json_schema_extra = {
      "example": {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe",
        "full_name": "홍길동",
        "is_active": True,
        "is_superuser": False,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
      }
    }


class UserInDB(UserBase):
  """
  데이터베이스 사용자 스키마

  내부적으로 사용되며, 해싱된 비밀번호를 포함합니다.
  """

  id: int
  hashed_password: str
  is_active: bool
  is_superuser: bool
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True
