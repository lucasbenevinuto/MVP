from typing import List, Optional, Dict, Any, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.property import Property, PropertyUpdate
from app.schemas.property import (
    PropertyCreate, PropertyUpdate as PropertyUpdateSchema,
    PropertyUpdateCreate, PropertyUpdateUpdate as PropertyUpdateUpdateSchema
)


class CRUDProperty(CRUDBase[Property, PropertyCreate, PropertyUpdateSchema]):
    def get_by_name_and_project(self, db: Session, *, name: str, project_id: int) -> Optional[Property]:
        return db.query(Property).filter(Property.name == name, Property.project_id == project_id).first()
    
    def get_project_properties(self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100) -> List[Property]:
        return db.query(Property).filter(Property.project_id == project_id).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Property]:
        return db.query(Property).filter(Property.status == status).offset(skip).limit(limit).all()
    
    def get_sold_properties(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Property]:
        return db.query(Property).filter(Property.is_sold == True).offset(skip).limit(limit).all()
    
    def get_available_properties(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Property]:
        return db.query(Property).filter(Property.is_sold == False).offset(skip).limit(limit).all()


class CRUDPropertyUpdate(CRUDBase[PropertyUpdate, PropertyUpdateCreate, PropertyUpdateUpdateSchema]):
    def get_property_updates(self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100) -> List[PropertyUpdate]:
        return db.query(PropertyUpdate).filter(PropertyUpdate.property_id == property_id).offset(skip).limit(limit).all()
    
    def get_user_updates(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[PropertyUpdate]:
        return db.query(PropertyUpdate).filter(PropertyUpdate.user_id == user_id).offset(skip).limit(limit).all()


property = CRUDProperty(Property)
property_update = CRUDPropertyUpdate(PropertyUpdate) 