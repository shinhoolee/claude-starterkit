FastAPI 백엔드 API Starter Kit 구현 계획

     프로젝트 개요

     목표: FastAPI 기반의 재사용 가능한 백엔드 API Starter Kit 구축

     기술 스택:
     - 프레임워크: FastAPI (Python 3.11+)
     - 데이터베이스: PostgreSQL
     - ORM: SQLAlchemy 2.0
     - 인증: JWT (python-jose, passlib)
     - 의존성 관리: Poetry
     - 마이그레이션: Alembic
     - 컨테이너: Docker & Docker Compose

     핵심 기능:`
     - ✅ 환경변수 관리 (pydantic-settings)
     - ✅ 전역 에러 핸들링
     - ✅ 구조화된 로깅 시스템
     - ✅ PostgreSQL 연결 및 세션 관리
     - ✅ JWT 기반 인증/인가
     - ✅ API 문서화 (Swagger/OpenAPI 자동 생성)
     - ✅ 레이어드 아키텍처 (Router → Service → Repository)
     - ✅ DTO 패턴 (Pydantic 모델)
     - ✅ 의존성 주입 (FastAPI Depends)
     - ✅ CORS 설정
     - ✅ Health Check 엔드포인트
     - ✅ 표준 API 응답 형식
     - ✅ 테스트 구조 (pytest)

     프로젝트 디렉토리 구조

     claude-starterkit/
     ├── .env.example                    # 환경변수 샘플
     ├── .gitignore
     ├── Dockerfile
     ├── docker-compose.yml
     ├── pyproject.toml                  # Poetry 의존성
     ├── poetry.lock
     ├── README.md
     ├── alembic.ini                     # DB 마이그레이션
     │
     ├── app/                            # 애플리케이션 루트
     │   ├── __init__.py
     │   ├── main.py                     # FastAPI 진입점 ⭐
     │   │
     │   ├── core/                       # 핵심 설정
     │   │   ├── config.py               # 환경변수 관리 ⭐
     │   │   ├── database.py             # DB 연결 및 세션 ⭐
     │   │   ├── security.py             # JWT 및 암호화 ⭐
     │   │   ├── logging.py              # 로깅 설정
     │   │   └── exceptions.py           # 커스텀 예외
     │   │
     │   ├── models/                     # SQLAlchemy 모델
     │   │   ├── base.py                 # Base 모델
     │   │   ├── user.py                 # User 모델
     │   │   └── post.py                 # Post 모델 (샘플)
     │   │
     │   ├── schemas/                    # Pydantic DTO
     │   │   ├── common.py               # 공통 응답 스키마
     │   │   ├── user.py
     │   │   ├── post.py
     │   │   └── auth.py
     │   │
     │   ├── repositories/               # 데이터 접근 계층
     │   │   ├── base.py                 # Generic Repository
     │   │   ├── user.py
     │   │   └── post.py
     │   │
     │   ├── services/                   # 비즈니스 로직
     │   │   ├── user.py
     │   │   ├── post.py
     │   │   └── auth.py
     │   │
     │   ├── api/                        # API 라우터
     │   │   ├── deps.py                 # 공통 의존성 ⭐
     │   │   └── v1/
     │   │       ├── router.py           # 라우터 통합
     │   │       ├── auth.py
     │   │       ├── users.py
     │   │       ├── posts.py
     │   │       └── health.py
     │   │
     │   ├── middleware/                 # 미들웨어
     │   │   ├── error_handler.py        # 전역 예외 핸들러
     │   │   └── logging_middleware.py   # 요청/응답 로깅
     │   │
     │   └── utils/                      # 유틸리티
     │       ├── response.py             # 응답 헬퍼
     │       └── pagination.py
     │
     ├── alembic/                        # 마이그레이션
     │   ├── versions/
     │   └── env.py
     │
     ├── tests/                          # 테스트
     │   ├── conftest.py
     │   ├── test_api/
     │   ├── test_services/
     │   └── test_repositories/
     │
     └── scripts/                        # 유틸리티 스크립트
         ├── init_db.py
         └── create_superuser.py

     아키텍처 설계

     레이어드 아키텍처 (3계층)

     1. Router (API) 계층

     책임: HTTP 요청/응답 처리
     - HTTP 라우팅
     - 입력 검증 (Pydantic)
     - 의존성 주입 (인증, DB 세션)
     - Service 계층 호출
     - HTTP 응답 생성

     2. Service 계층

     책임: 비즈니스 로직
     - 비즈니스 규칙 구현
     - 트랜잭션 관리
     - 여러 Repository 조합
     - 데이터 변환 (Model ↔ DTO)
     - 비즈니스 예외 처리

     3. Repository 계층

     책임: 데이터베이스 접근
     - CRUD 작업
     - 쿼리 최적화
     - DB 특화 로직
     - 원시 데이터 반환

     의존성 흐름

     Router (FastAPI)
       ↓ Depends(get_current_user, get_db)
     Service (비즈니스 로직)
       ↓ Repository 호출
     Repository (데이터 접근)
       ↓ SQLAlchemy Session
     Database (PostgreSQL)

     JWT 인증/인가 시스템

     토큰 구조

     - Access Token: 30분 유효 (API 요청 시 사용)
     - Refresh Token: 7일 유효 (Access Token 갱신)

     인증 플로우

     1. 회원가입: POST /api/v1/users → 이메일 중복 체크 → 비밀번호 해싱 → DB 저장
     2. 로그인: POST /api/v1/auth/login → 이메일/비밀번호 검증 → Access/Refresh Token 발급
     3. 인증 필요 API: Header에 Authorization: Bearer {token} → JWT 검증 → 사용자 정보 조회
     4. 토큰 갱신: POST /api/v1/auth/refresh → Refresh Token 검증 → 새 Access Token 발급

     인증 의존성 (app/api/deps.py)

     async def get_current_user(
       credentials: HTTPAuthorizationCredentials = Depends(security),
       db: Session = Depends(get_db)
     ) -> User:
       # JWT 토큰 검증
       # 사용자 존재 및 활성 상태 확인
       # User 객체 반환

     에러 핸들링 전략

     커스텀 예외 계층

     BaseAPIException (기본 예외)
       ├── EntityNotFoundException (404)
       ├── DuplicateEntityException (409)
       ├── UnauthorizedException (401)
       ├── ForbiddenException (403)
       ├── ValidationException (422)
       └── DatabaseException (500)

     전역 예외 핸들러

     - BaseAPIException → 커스텀 예외 처리
     - RequestValidationError → Pydantic 유효성 검증 실패
     - SQLAlchemyError → DB 에러
     - Exception → 일반 예외 (최종 안전망)

     표준 에러 응답

     {
       "success": false,
       "message": "에러 메시지",
       "error_code": "ENTITY_NOT_FOUND",
       "details": {...},
       "data": null
     }

     로깅 시스템

     로그 레벨

     - INFO: 일반 요청/응답, 애플리케이션 이벤트
     - WARNING: Pydantic 유효성 검증 실패
     - ERROR: DB 에러, 핸들링된 예외
     - CRITICAL: 핸들링되지 않은 예외

     로그 출력

     - 콘솔: 개발 환경용
     - 파일 (app.log): 모든 로그 (로테이션 10MB)
     - 파일 (error.log): ERROR 이상만 (로테이션 10MB)

     로깅 미들웨어

     - 요청 정보 (method, path, client IP, user agent)
     - 응답 시간 측정
     - 상태 코드 기록

     환경변수 관리

     설정 파일: app/core/config.py

     - pydantic-settings를 사용한 타입 안전 설정
     - .env 파일에서 자동 로드
     - 유효성 검증 (최소 길이, 필수 값 등)

     주요 환경변수

     # 애플리케이션
     ENV=development
     DEBUG=true
     SECRET_KEY=your-secret-key-minimum-32-characters

     # 데이터베이스
     DATABASE_URL=postgresql://postgres:password@localhost:5432/starterkit_dev

     # JWT
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     REFRESH_TOKEN_EXPIRE_DAYS=7

     # CORS
     CORS_ORIGINS=http://localhost:3000,http://localhost:8080

     데이터베이스 설계

     User 모델 (예시)

     class User(Base):
       __tablename__ = "users"

       id: int (PK)
       email: str (unique, indexed)
       username: str (unique, indexed)
       hashed_password: str
       full_name: str (nullable)
       is_active: bool (default=True)
       is_superuser: bool (default=False)
       created_at: datetime
       updated_at: datetime

     Post 모델 (샘플)

     class Post(Base):
       __tablename__ = "posts"

       id: int (PK)
       title: str
       content: str
       author_id: int (FK → users.id)
       is_published: bool (default=False)
       created_at: datetime
       updated_at: datetime

     마이그레이션 워크플로우

     1. 모델 생성/수정
     2. alembic revision --autogenerate -m "메시지"
     3. alembic upgrade head

     표준 API 응답 형식

     성공 응답

     {
       "success": true,
       "message": "요청이 성공했습니다.",
       "data": {...},
       "error_code": null,
       "details": null
     }

     페이지네이션 응답

     {
       "success": true,
       "message": "조회 성공",
       "data": [...],
       "meta": {
         "total": 100,
         "page": 1,
         "page_size": 20,
         "total_pages": 5,
         "has_next": true,
         "has_prev": false
       }
     }

     구현 단계별 계획

     Phase 1: 프로젝트 기반 구축

     파일: 11개

     1. 프로젝트 디렉토리 구조 생성
     2. pyproject.toml - Poetry 의존성 정의
     3. .env.example - 환경변수 샘플
     4. .gitignore
     5. app/core/config.py - 환경변수 관리
     6. app/core/logging.py - 로깅 설정
     7. app/core/database.py - DB 연결
     8. app/models/base.py - Base 모델
     9. Dockerfile
     10. docker-compose.yml
     11. README.md (기본)

     검증:
     - docker-compose up 실행
     - PostgreSQL 연결 확인

     Phase 2: 에러 핸들링 및 공통 모듈

     파일: 5개

     1. app/core/exceptions.py - 커스텀 예외 클래스
     2. app/middleware/error_handler.py - 전역 예외 핸들러
     3. app/middleware/logging_middleware.py - 로깅 미들웨어
     4. app/schemas/common.py - 표준 응답 스키마
     5. app/utils/response.py - 응답 헬퍼

     검증:
     - 의도적 예외 발생 → 표준 에러 응답 확인

     Phase 3: 인증 시스템 구현

     파일: 11개

     1. app/core/security.py - JWT 및 비밀번호 해싱
     2. app/models/user.py - User 모델
     3. app/schemas/user.py - User DTO (Request/Response)
     4. app/schemas/auth.py - Auth DTO (Login, Token)
     5. app/repositories/base.py - Generic Repository 패턴
     6. app/repositories/user.py - UserRepository
     7. app/services/user.py - UserService
     8. app/services/auth.py - AuthService
     9. app/api/deps.py - 인증 의존성
     10. app/api/v1/auth.py - Auth 엔드포인트
     11. app/api/v1/users.py - User 엔드포인트

     검증:
     - 회원가입 → 로그인 → 인증 필요 API 호출 플로우 테스트

     Phase 4: 메인 애플리케이션 통합

     파일: 3개

     1. app/api/v1/health.py - Health check
     2. app/api/v1/router.py - 라우터 통합
     3. app/main.py - FastAPI 앱 진입점 (미들웨어, CORS, 예외 핸들러 등록)

     검증:
     - Swagger UI 접속 (http://localhost:8000/docs)
     - Health check: GET /api/v1/health

     Phase 5: 데이터베이스 마이그레이션

     파일: 3개

     1. alembic.ini - Alembic 설정
     2. alembic/env.py - 마이그레이션 환경
     3. scripts/init_db.py - DB 초기화 스크립트

     검증:
     - alembic revision --autogenerate -m "Initial migration"
     - alembic upgrade head
     - PostgreSQL 테이블 생성 확인

     Phase 6: 샘플 기능 (Post CRUD)

     파일: 5개

     1. app/models/post.py - Post 모델
     2. app/schemas/post.py - Post DTO
     3. app/repositories/post.py - PostRepository
     4. app/services/post.py - PostService
     5. app/api/v1/posts.py - Post 엔드포인트

     검증:
     - POST /api/v1/posts (생성)
     - GET /api/v1/posts (목록)
     - GET /api/v1/posts/{id} (조회)
     - PUT /api/v1/posts/{id} (수정)
     - DELETE /api/v1/posts/{id} (삭제)

     Phase 7: 테스트 구조

     파일: 4개

     1. tests/conftest.py - pytest 설정 및 fixture
     2. tests/test_api/test_auth.py
     3. tests/test_api/test_users.py
     4. tests/test_services/test_user_service.py

     검증:
     - pytest 실행 → 모든 테스트 통과

     Phase 8: 문서화 및 마무리

     파일: 2개

     1. README.md (완성) - 프로젝트 소개, 설치, 실행, API 문서 링크
     2. scripts/create_superuser.py - 관리자 생성 스크립트

     핵심 파일 5개 (Critical Files)

     구현 시 가장 먼저 작성해야 할 파일:

     1. app/core/config.py - 전체 애플리케이션 설정의 중심
     2. app/core/database.py - DB 연결 및 세션 관리
     3. app/core/security.py - JWT 인증의 핵심
     4. app/main.py - 애플리케이션 진입점
     5. app/api/deps.py - 인증 및 DB 세션 의존성

     주요 의존성 (pyproject.toml)

     [tool.poetry.dependencies]
     python = "^3.11"
     fastapi = "^0.109.0"
     uvicorn = {extras = ["standard"], version = "^0.27.0"}
     pydantic = "^2.5.0"
     pydantic-settings = "^2.1.0"
     sqlalchemy = "^2.0.25"
     psycopg2-binary = "^2.9.9"
     alembic = "^1.13.1"
     python-jose = {extras = ["cryptography"], version = "^3.3.0"}
     passlib = {extras = ["bcrypt"], version = "^1.7.4"}
     python-multipart = "^0.0.6"

     [tool.poetry.group.dev.dependencies]
     pytest = "^7.4.4"
     pytest-asyncio = "^0.23.3"
     httpx = "^0.26.0"
     black = "^24.1.1"

     API 엔드포인트 목록

     인증 (/api/v1/auth)

     - POST /auth/login - 로그인 (이메일, 비밀번호)
     - POST /auth/refresh - 토큰 갱신
     - POST /auth/logout - 로그아웃
     - GET /auth/me - 현재 사용자 정보

     사용자 (/api/v1/users)

     - POST /users - 회원가입 (공개)
     - GET /users - 사용자 목록 (인증 필요)
     - GET /users/{id} - 특정 사용자 조회 (인증 필요)
     - PUT /users/{id} - 사용자 수정 (인증 필요)
     - DELETE /users/{id} - 사용자 삭제 (관리자)

     게시물 (/api/v1/posts) - 샘플

     - POST /posts - 게시물 생성 (인증 필요)
     - GET /posts - 게시물 목록 (공개)
     - GET /posts/{id} - 게시물 조회 (공개)
     - PUT /posts/{id} - 게시물 수정 (작성자 또는 관리자)
     - DELETE /posts/{id} - 게시물 삭제 (작성자 또는 관리자)

     헬스체크 (/api/v1/health)

     - GET /health - 애플리케이션 및 DB 상태 확인

     코딩 컨벤션

     Python 스타일

     - 네이밍: snake_case (Python PEP 8 표준)
       - 변수/함수: user_service, get_user_by_id
       - 클래스: UserService, BaseRepository
       - 상수: ACCESS_TOKEN_EXPIRE_MINUTES
     - 들여쓰기: 2칸 (사용자 요구사항)
     - 주석: 한국어 작성
     - Docstring: 함수 설명 한국어
     - 타입 힌팅: 모든 함수에 타입 명시

     커밋 메시지

     - 한국어로 작성
     - 예: "feat: JWT 인증 시스템 구현", "fix: 사용자 중복 체크 버그 수정"

     실행 방법

     로컬 개발 (Docker Compose)

     # 환경변수 설정
     cp .env.example .env

     # Docker Compose로 실행
     docker-compose up

     # 마이그레이션
     docker-compose exec api alembic upgrade head

     # 관리자 생성
     docker-compose exec api python scripts/create_superuser.py

     수동 실행

     # Poetry 설치
     curl -sSL https://install.python-poetry.org | python3 -

     # 의존성 설치
     poetry install

     # 환경변수 설정
     cp .env.example .env

     # PostgreSQL 실행 (Docker)
     docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15

     # 마이그레이션
     poetry run alembic upgrade head

     # 애플리케이션 실행
     poetry run uvicorn app.main:app --reload

     테스트

     poetry run pytest

     성공 기준

     - ✅ Docker Compose로 한 번에 실행 가능
     - ✅ Swagger UI에서 모든 API 테스트 가능
     - ✅ JWT 인증이 정상 작동
     - ✅ 에러가 표준 형식으로 반환됨
     - ✅ 로그가 파일 및 콘솔에 정상 출력
     - ✅ 마이그레이션이 정상 동작
     - ✅ 테스트가 모두 통과
     - ✅ README에 명확한 사용법 문서화

     예상 총 파일 수

     약 40-45개 파일:
     - Python 파일: ~30개
     - 설정 파일: ~8개
     - 테스트 파일: ~5개
     - 문서/스크립트: ~3개

     ---