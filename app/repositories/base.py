"""
Generic Repository 패턴

재사용 가능한 기본 CRUD 작업을 제공하는 베이스 Repository입니다.
"""
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.models.base import Base

# 제네릭 타입 변수 (SQLAlchemy 모델)
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
  """
  기본 Repository 클래스

  모든 모델에 대한 공통 CRUD 작업을 제공합니다.

  Attributes:
    model: SQLAlchemy 모델 클래스
  """

  def __init__(self, model: Type[ModelType]):
    """
    Repository 초기화

    Args:
      model: SQLAlchemy 모델 클래스
    """
    self.model = model

  def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
    """
    ID로 단일 레코드 조회

    Args:
      db: 데이터베이스 세션
      id: 조회할 레코드의 ID

    Returns:
      Optional[ModelType]: 조회된 레코드 (없으면 None)
    """
    return db.query(self.model).filter(self.model.id == id).first()

  def get_multi(
    self,
    db: Session,
    skip: int = 0,
    limit: int = 100
  ) -> List[ModelType]:
    """
    여러 레코드 조회 (페이지네이션)

    Args:
      db: 데이터베이스 세션
      skip: 건너뛸 레코드 수
      limit: 조회할 최대 레코드 수

    Returns:
      List[ModelType]: 조회된 레코드 리스트
    """
    return db.query(self.model).offset(skip).limit(limit).all()

  def get_all(self, db: Session) -> List[ModelType]:
    """
    모든 레코드 조회

    Args:
      db: 데이터베이스 세션

    Returns:
      List[ModelType]: 모든 레코드 리스트
    """
    return db.query(self.model).all()

  def count(self, db: Session) -> int:
    """
    전체 레코드 수 조회

    Args:
      db: 데이터베이스 세션

    Returns:
      int: 전체 레코드 수
    """
    return db.query(self.model).count()

  def create(self, db: Session, obj_in: Dict[str, Any]) -> ModelType:
    """
    새 레코드 생성

    Args:
      db: 데이터베이스 세션
      obj_in: 생성할 데이터 딕셔너리

    Returns:
      ModelType: 생성된 레코드
    """
    db_obj = self.model(**obj_in)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

  def update(
    self,
    db: Session,
    db_obj: ModelType,
    obj_in: Dict[str, Any]
  ) -> ModelType:
    """
    기존 레코드 수정

    Args:
      db: 데이터베이스 세션
      db_obj: 수정할 기존 레코드
      obj_in: 수정할 데이터 딕셔너리

    Returns:
      ModelType: 수정된 레코드
    """
    # None이 아닌 값만 업데이트
    for field, value in obj_in.items():
      if value is not None and hasattr(db_obj, field):
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj

  def delete(self, db: Session, id: int) -> Optional[ModelType]:
    """
    레코드 삭제

    Args:
      db: 데이터베이스 세션
      id: 삭제할 레코드의 ID

    Returns:
      Optional[ModelType]: 삭제된 레코드 (없으면 None)
    """
    obj = self.get_by_id(db, id)
    if obj:
      db.delete(obj)
      db.commit()
    return obj

  def get_by_field(
    self,
    db: Session,
    field_name: str,
    value: Any
  ) -> Optional[ModelType]:
    """
    특정 필드 값으로 단일 레코드 조회

    Args:
      db: 데이터베이스 세션
      field_name: 필드 이름
      value: 조회할 값

    Returns:
      Optional[ModelType]: 조회된 레코드 (없으면 None)
    """
    return db.query(self.model).filter(
      getattr(self.model, field_name) == value
    ).first()

  def get_multi_by_field(
    self,
    db: Session,
    field_name: str,
    value: Any,
    skip: int = 0,
    limit: int = 100
  ) -> List[ModelType]:
    """
    특정 필드 값으로 여러 레코드 조회

    Args:
      db: 데이터베이스 세션
      field_name: 필드 이름
      value: 조회할 값
      skip: 건너뛸 레코드 수
      limit: 조회할 최대 레코드 수

    Returns:
      List[ModelType]: 조회된 레코드 리스트
    """
    return db.query(self.model).filter(
      getattr(self.model, field_name) == value
    ).offset(skip).limit(limit).all()

  def exists(self, db: Session, id: int) -> bool:
    """
    레코드 존재 여부 확인

    Args:
      db: 데이터베이스 세션
      id: 확인할 레코드의 ID

    Returns:
      bool: 존재하면 True, 없으면 False
    """
    return db.query(self.model).filter(self.model.id == id).first() is not None
