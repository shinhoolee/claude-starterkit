# FastAPI Starter Kit

FastAPI 기반의 재사용 가능한 백엔드 API 프로젝트 템플릿입니다.

## 기술 스택

- **프레임워크**: FastAPI (Python 3.11+)
- **데이터베이스**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **인증**: JWT (python-jose, passlib)
- **의존성 관리**: Poetry
- **컨테이너**: Docker & Docker Compose

## 주요 기능

- ✅ 환경변수 관리 (pydantic-settings)
- ✅ 전역 에러 핸들링
- ✅ 구조화된 로깅 시스템
- ✅ PostgreSQL 연결 및 세션 관리
- ✅ 레이어드 아키텍처 (Router → Service → Repository)
- ✅ Docker Compose 기반 개발 환경

## 빠른 시작

### 1. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 `SECRET_KEY`를 32자 이상의 랜덤 문자열로 변경하세요.

### 2. Docker Compose로 실행

```bash
docker-compose up --build
```

### 3. 접속 확인

- API 서버: http://localhost:8000
- PostgreSQL: localhost:5432

## 프로젝트 구조

```
claude-starterkit/
├── app/
│   ├── core/
│   │   ├── config.py       # 환경변수 관리
│   │   ├── database.py     # DB 연결
│   │   └── logging.py      # 로깅 설정
│   └── models/
│       └── base.py         # Base 모델
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## 현재 구현 상태

**Phase 1: 프로젝트 기반 구축 ✅**
- 디렉토리 구조
- Poetry 의존성 설정
- Docker 환경
- 환경변수 관리
- DB 연결 설정
- 로깅 시스템

## 다음 단계

**Phase 2: 에러 핸들링 및 공통 모듈**
- 커스텀 예외 클래스
- 전역 예외 핸들러
- 표준 API 응답 형식

**Phase 3: 인증 시스템**
- JWT 기반 인증/인가
- 회원가입/로그인
- User 모델 및 Repository

**Phase 4: 메인 애플리케이션 통합**
- FastAPI 앱 진입점 (app/main.py)
- Health check 엔드포인트
- Swagger UI

## 개발 환경

### Poetry 사용 (로컬)

```bash
# Poetry 설치
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install

# 개발 서버 실행
poetry run uvicorn app.main:app --reload
```

### PostgreSQL 직접 실행

```bash
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=starterkit_dev \
  postgres:15
```

## 라이선스

MIT
