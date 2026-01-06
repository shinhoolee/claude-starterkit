"""
데이터베이스 초기화 스크립트

SQLAlchemy를 사용하여 모든 테이블을 생성합니다.
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import engine
from app.models.base import Base
from app.models.user import User

def init_db():
  """데이터베이스 테이블 생성"""
  print("데이터베이스 테이블 생성 중...")

  # 모든 테이블 생성
  Base.metadata.create_all(bind=engine)

  print("✅ 데이터베이스 테이블 생성 완료!")
  print(f"생성된 테이블: {list(Base.metadata.tables.keys())}")

if __name__ == "__main__":
  init_db()
