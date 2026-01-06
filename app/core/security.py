"""
보안 관련 유틸리티

JWT 토큰 생성/검증 및 비밀번호 해싱 기능을 제공합니다.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 비밀번호 해싱 컨텍스트 (bcrypt 알고리즘 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 알고리즘
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
  """
  비밀번호를 bcrypt로 해싱합니다.

  Args:
    password: 평문 비밀번호

  Returns:
    str: 해싱된 비밀번호

  Example:
    >>> hashed = hash_password("mypassword123")
    >>> print(hashed)
    $2b$12$...
  """
  return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
  """
  평문 비밀번호와 해싱된 비밀번호를 비교합니다.

  Args:
    plain_password: 평문 비밀번호
    hashed_password: 해싱된 비밀번호

  Returns:
    bool: 일치하면 True, 불일치하면 False

  Example:
    >>> hashed = hash_password("mypassword123")
    >>> verify_password("mypassword123", hashed)
    True
    >>> verify_password("wrongpassword", hashed)
    False
  """
  return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
  subject: str,
  expires_delta: Optional[timedelta] = None,
  additional_claims: Optional[Dict[str, Any]] = None
) -> str:
  """
  JWT Access Token을 생성합니다.

  Args:
    subject: 토큰의 주체 (보통 사용자 ID 또는 이메일)
    expires_delta: 토큰 만료 시간 (기본값: 설정 파일의 ACCESS_TOKEN_EXPIRE_MINUTES)
    additional_claims: 추가 클레임 (선택사항)

  Returns:
    str: JWT 토큰 문자열

  Example:
    >>> token = create_access_token(subject="user@example.com")
    >>> print(token)
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  """
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(
      minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

  # 기본 클레임
  to_encode = {
    "exp": expire,
    "sub": str(subject),
    "iat": datetime.utcnow(),
    "type": "access"
  }

  # 추가 클레임이 있으면 병합
  if additional_claims:
    to_encode.update(additional_claims)

  # JWT 토큰 생성
  encoded_jwt = jwt.encode(
    to_encode,
    settings.SECRET_KEY,
    algorithm=ALGORITHM
  )

  return encoded_jwt


def create_refresh_token(
  subject: str,
  expires_delta: Optional[timedelta] = None
) -> str:
  """
  JWT Refresh Token을 생성합니다.

  Args:
    subject: 토큰의 주체 (보통 사용자 ID 또는 이메일)
    expires_delta: 토큰 만료 시간 (기본값: 설정 파일의 REFRESH_TOKEN_EXPIRE_DAYS)

  Returns:
    str: JWT 토큰 문자열

  Example:
    >>> token = create_refresh_token(subject="user@example.com")
    >>> print(token)
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  """
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(
      days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

  to_encode = {
    "exp": expire,
    "sub": str(subject),
    "iat": datetime.utcnow(),
    "type": "refresh"
  }

  encoded_jwt = jwt.encode(
    to_encode,
    settings.SECRET_KEY,
    algorithm=ALGORITHM
  )

  return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
  """
  JWT 토큰을 디코딩하고 검증합니다.

  Args:
    token: JWT 토큰 문자열

  Returns:
    Optional[Dict[str, Any]]: 디코딩된 페이로드 (검증 실패 시 None)

  Example:
    >>> token = create_access_token(subject="user@example.com")
    >>> payload = decode_token(token)
    >>> print(payload["sub"])
    user@example.com
  """
  try:
    payload = jwt.decode(
      token,
      settings.SECRET_KEY,
      algorithms=[ALGORITHM]
    )
    return payload
  except JWTError:
    return None


def get_token_subject(token: str) -> Optional[str]:
  """
  JWT 토큰에서 subject(주체)를 추출합니다.

  Args:
    token: JWT 토큰 문자열

  Returns:
    Optional[str]: 토큰의 subject (검증 실패 시 None)

  Example:
    >>> token = create_access_token(subject="user@example.com")
    >>> subject = get_token_subject(token)
    >>> print(subject)
    user@example.com
  """
  payload = decode_token(token)
  if payload:
    return payload.get("sub")
  return None


def verify_token_type(token: str, expected_type: str) -> bool:
  """
  토큰의 타입(access/refresh)을 검증합니다.

  Args:
    token: JWT 토큰 문자열
    expected_type: 예상되는 토큰 타입 ("access" 또는 "refresh")

  Returns:
    bool: 토큰 타입이 일치하면 True, 불일치하거나 검증 실패 시 False

  Example:
    >>> access_token = create_access_token(subject="user@example.com")
    >>> verify_token_type(access_token, "access")
    True
    >>> verify_token_type(access_token, "refresh")
    False
  """
  payload = decode_token(token)
  if payload:
    return payload.get("type") == expected_type
  return False
