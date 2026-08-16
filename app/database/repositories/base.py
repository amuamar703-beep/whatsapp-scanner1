from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.flush()
        return instance

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.get(self.model, id)

    def get_by(self, **filters) -> Optional[ModelType]:
        stmt = select(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(self, **filters) -> List[ModelType]:
        stmt = select(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        return self.db.execute(stmt).scalars().all()

    def list_paginated(self, page: int = 1, per_page: int = 20, **filters) -> tuple[List[ModelType], int]:
        offset = (page - 1) * per_page
        stmt = select(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar()
        
        stmt = stmt.offset(offset).limit(per_page)
        items = self.db.execute(stmt).scalars().all()
        
        return items, total

    def update(self, id: Any, **kwargs) -> Optional[ModelType]:
        instance = self.get(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.flush()
        return instance

    def delete(self, id: Any) -> bool:
        instance = self.get(id)
        if instance:
            self.db.delete(instance)
            self.db.flush()
            return True
        return False

    def count(self, **filters) -> int:
        stmt = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        return self.db.execute(stmt).scalar()