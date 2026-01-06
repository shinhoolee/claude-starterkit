---
description: '개발 환경 및 프로젝트 상태를 검증하고 문제를 자동으로 해결합니다'
allowed-tools:
  [
    'Bash(poetry:*)',
    'Bash(npm:*)',
    'Bash(docker:*)',
    'Bash(psql:*)',
    'Bash(curl:*)',
    'Bash(alembic:*)',
    'Read',
    'Glob',
  ]
---

# Claude 명령어: Health Check

개발 환경 및 프로젝트 상태를 검증하고 문제를 발견하면 자동으로 해결 방법을 제시합니다.

## 사용법

```
/health-check
```

## 검증 항목

### 1. 환경변수 검증
- `.env` 파일 존재 여부
- `.env.example`과 비교하여 누락된 변수 확인
- 필수 변수 값 설정 여부 (SECRET_KEY, DATABASE_URL 등)
- 문제 발견 시: 누락된 변수 목록 제시 및 자동 생성 옵션 제공

### 2. 데이터베이스 연결
- PostgreSQL 컨테이너 실행 상태 확인
- 데이터베이스 연결 테스트
- 마이그레이션 상태 확인 (pending migrations)
- 문제 발견 시: Docker 컨테이너 시작 또는 마이그레이션 실행 제안

### 3. 의존성 확인
- **FastAPI (Python)**: Poetry 의존성 설치 여부
- **Express (Node.js)**: npm/yarn 의존성 설치 여부
- pyproject.toml / package.json과 실제 설치 상태 비교
- 문제 발견 시: 설치 명령어 제시 또는 자동 설치 옵션

### 4. 포트 충돌 확인
- FastAPI 포트 (기본: 8000) 사용 가능 여부
- Express 포트 (기본: 3000) 사용 가능 여부
- 문제 발견 시: 충돌하는 프로세스 정보 제공 및 종료 옵션

### 5. Docker 상태
- Docker 데몬 실행 여부
- docker-compose.yml에 정의된 컨테이너 상태
- 문제 발견 시: 컨테이너 시작 명령어 제시

### 6. API 엔드포인트 확인
- FastAPI Health Check 엔드포인트 응답 확인
- Express Health Check 엔드포인트 응답 확인
- 문제 발견 시: 서버 시작 필요 알림

## 프로세스

1. **환경변수 검증**
   - .env 파일 읽기
   - .env.example과 비교
   - 누락/빈 값 감지

2. **데이터베이스 확인**
   - Docker 컨테이너 상태 확인
   - psql 연결 테스트
   - Alembic 마이그레이션 상태 확인

3. **의존성 확인**
   - poetry.lock 존재 여부
   - node_modules 폴더 존재 여부
   - 실제 패키지 설치 확인

4. **포트 확인**
   - netstat 또는 lsof로 포트 사용 확인
   - 충돌 시 프로세스 정보 제공

5. **서비스 상태 확인**
   - curl로 /health 엔드포인트 호출
   - 응답 코드 및 내용 검증

6. **결과 리포트**
   - ✅ 정상 항목
   - ❌ 문제 항목 및 해결 방법
   - 자동 수정 가능한 항목은 실행 옵션 제공

## 출력 예시

```
🔍 개발 환경 검증 시작...

✅ 환경변수
  - .env 파일 존재
  - 모든 필수 변수 설정됨

❌ 데이터베이스
  - PostgreSQL 컨테이너 실행 중이 아님
  → 해결: docker-compose up -d postgres

✅ 의존성
  - Python: poetry.lock 최신 상태
  - Node.js: node_modules 설치됨

⚠️  포트
  - 포트 8000: 사용 가능
  - 포트 3000: 사용 중 (PID: 1234, node)
  → 해결: kill 1234 또는 다른 포트 사용

❌ 서비스
  - FastAPI: 응답 없음 (서버 미실행)
  - Express: 응답 없음 (서버 미실행)
  → 해결: uvicorn app.main:app --reload

---
문제를 자동으로 수정하시겠습니까? (y/n)
```

## 자동 수정 기능

사용자 동의 시 다음 작업을 자동으로 수행:
- 누락된 환경변수 파일 생성
- Docker 컨테이너 시작
- 의존성 설치
- 마이그레이션 실행

## 주의사항

- 프로덕션 환경에서는 사용하지 마세요 (개발 환경 전용)
- 자동 수정 전 항상 사용자 확인을 받습니다
- 민감한 정보(비밀번호 등)는 로그에 출력하지 않습니다
