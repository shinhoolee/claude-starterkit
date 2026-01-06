---
description: 'DB 모델 변경사항을 감지하고 마이그레이션을 자동으로 생성합니다'
allowed-tools:
  [
    'Bash(alembic:*)',
    'Bash(git diff:*)',
    'Bash(python:*)',
    'Read',
    'Glob',
    'Grep',
  ]
---

# Claude 명령어: Sync Models

데이터베이스 모델 변경사항을 자동으로 감지하고 마이그레이션 파일을 생성합니다.

## 사용법

```
/sync-models
```

## 프로세스

1. **모델 변경 감지**
   - app/models/ 폴더의 SQLAlchemy 모델 파일 스캔
   - git diff로 마지막 커밋 이후 변경사항 확인
   - 새로운 필드, 테이블, 인덱스, 제약조건 분석

2. **변경사항 분석**
   - 추가된 필드 및 타입
   - 삭제된 필드
   - 변경된 필드 (타입, nullable, default 등)
   - 새로운 테이블
   - 인덱스 및 제약조건 변경

3. **마이그레이션 생성**
   - Alembic autogenerate로 마이그레이션 스크립트 생성
   - 변경사항 기반으로 의미있는 메시지 자동 작성
   - 예: "add_email_to_users", "create_posts_table"

4. **프리뷰 제공**
   - 생성될 마이그레이션 파일 내용 표시
   - upgrade() 함수 확인
   - downgrade() 함수 확인 (롤백 스크립트)

5. **사용자 확인**
   - 마이그레이션 적용 여부 선택
   - 적용 시: alembic upgrade head 실행
   - 취소 시: 마이그레이션 파일만 생성

## 마이그레이션 메시지 자동 생성 규칙

### 테이블 관련
- 새 테이블 생성: `create_{table_name}_table`
- 테이블 삭제: `drop_{table_name}_table`
- 테이블 이름 변경: `rename_{old}_to_{new}_table`

### 필드 관련
- 필드 추가: `add_{field_name}_to_{table_name}`
- 필드 삭제: `remove_{field_name}_from_{table_name}`
- 필드 타입 변경: `change_{field_name}_type_in_{table_name}`
- 필드 이름 변경: `rename_{old}_to_{new}_in_{table_name}`

### 제약조건 관련
- 인덱스 추가: `add_index_on_{table_name}_{field_name}`
- 외래키 추가: `add_fk_{table_name}_{field_name}`
- Unique 제약조건: `add_unique_constraint_on_{table_name}`

### 복합 변경
- 여러 변경사항: `update_{table_name}_schema`
- 대규모 리팩토링: `refactor_database_schema`

## 출력 예시

```
🔍 모델 변경사항 감지 중...

📝 감지된 변경사항:
  [User 모델]
  + phone_number: String(20), nullable=True
  + is_verified: Boolean, default=False
  ~ email: unique=True 제약조건 추가

  [Post 모델]
  + published_at: DateTime, nullable=True
  - draft: Boolean (삭제됨)

---

📋 마이그레이션 생성 중...
  파일명: alembic/versions/20250106_1430_add_verification_fields_to_user.py
  메시지: "add verification fields to user and update post schema"

🔍 마이그레이션 프리뷰:

  def upgrade():
      # User 테이블 변경
      op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))
      op.add_column('users', sa.Column('is_verified', sa.Boolean(), default=False))
      op.create_unique_constraint('uq_users_email', 'users', ['email'])

      # Post 테이블 변경
      op.add_column('posts', sa.Column('published_at', sa.DateTime(), nullable=True))
      op.drop_column('posts', 'draft')

  def downgrade():
      # 롤백 스크립트
      op.drop_column('users', 'is_verified')
      op.drop_column('users', 'phone_number')
      op.drop_constraint('uq_users_email', 'users')
      op.add_column('posts', sa.Column('draft', sa.Boolean()))
      op.drop_column('posts', 'published_at')

---

✅ 마이그레이션 파일이 생성되었습니다.

마이그레이션을 바로 적용하시겠습니까? (y/n)
  y: alembic upgrade head 실행
  n: 나중에 수동으로 적용
```

## 적용 후 확인사항

마이그레이션 적용 후 다음을 자동으로 확인:
- ✅ 마이그레이션 성공 여부
- ✅ 데이터베이스 스키마 변경 확인
- ✅ 현재 마이그레이션 버전 표시
- ⚠️ 경고: 데이터 손실 가능성 있는 변경사항 알림

## 안전 기능

### 위험한 변경 감지
다음 변경사항은 경고와 함께 확인을 요청:
- 필드 삭제 (데이터 손실 가능)
- 필드 타입 변경 (데이터 변환 필요)
- NOT NULL 제약조건 추가 (기존 데이터 영향)
- 테이블 삭제 (전체 데이터 손실)

### 롤백 준비
- 항상 downgrade() 함수 생성
- 롤백 명령어 제공: `alembic downgrade -1`
- 마이그레이션 전 데이터베이스 백업 권장 메시지

### 프로덕션 주의사항
```
⚠️  경고: 프로덕션 환경에서는 다음을 권장합니다:
  1. 먼저 스테이징 환경에서 테스트
  2. 데이터베이스 백업 수행
  3. 다운타임 계획 수립
  4. 마이그레이션 스크립트 수동 검토
```

## 고급 옵션

### 빈 마이그레이션 생성
```
/sync-models --empty
→ 빈 마이그레이션 파일 생성 (수동 작성용)
```

### 특정 모델만 확인
```
/sync-models --model User
→ User 모델 변경사항만 확인
```

### 적용 없이 생성만
```
/sync-models --no-apply
→ 마이그레이션 파일만 생성하고 적용하지 않음
```

## 참고사항

- Alembic이 설치되고 설정되어 있어야 합니다
- alembic.ini 파일이 프로젝트 루트에 있어야 합니다
- 마이그레이션 전 항상 git으로 코드를 커밋하는 것을 권장합니다
- 복잡한 변경사항은 수동으로 마이그레이션 스크립트를 수정해야 할 수 있습니다
