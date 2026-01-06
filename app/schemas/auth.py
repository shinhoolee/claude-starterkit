"""
Auth DTO (Data Transfer Object)

인증 관련 요청/응답 스키마를 정의합니다.
"""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
  """
  로그인 요청 스키마

  이메일과 비밀번호로 로그인합니다.
  """

  email: EmailStr = Field(
    description="이메일 주소"
  )
  password: str = Field(
    min_length=1,
    description="비밀번호"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "email": "user@example.com",
        "password": "securepass123"
      }
    }


class TokenResponse(BaseModel):
  """
  토큰 응답 스키마

  로그인 성공 시 Access Token과 Refresh Token을 반환합니다.
  """

  access_token: str = Field(
    description="Access Token (API 요청에 사용)"
  )
  refresh_token: str = Field(
    description="Refresh Token (토큰 갱신에 사용)"
  )
  token_type: str = Field(
    default="bearer",
    description="토큰 타입"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
      }
    }


class RefreshTokenRequest(BaseModel):
  """
  토큰 갱신 요청 스키마

  Refresh Token을 사용하여 새로운 Access Token을 발급받습니다.
  """

  refresh_token: str = Field(
    description="Refresh Token"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
    }


class AccessTokenResponse(BaseModel):
  """
  Access Token 응답 스키마

  토큰 갱신 시 새로운 Access Token을 반환합니다.
  """

  access_token: str = Field(
    description="새로운 Access Token"
  )
  token_type: str = Field(
    default="bearer",
    description="토큰 타입"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
      }
    }
