from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.client import Lead
from app.schemas.client import LeadCreate, LeadUpdate


class CRUDLead(CRUDBase[Lead, LeadCreate, LeadUpdate]):
    def get_property_leads(
        self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lead]:
        """Get all leads for a property."""
        return (
            db.query(self.model)
            .filter(self.model.property_id == property_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_client_leads(
        self, db: Session, *, client_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lead]:
        """Get all leads for a client."""
        return (
            db.query(self.model)
            .filter(self.model.client_id == client_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_user_assigned_leads(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lead]:
        """Get all leads assigned to a user."""
        return (
            db.query(self.model)
            .filter(self.model.assigned_user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_company_leads(
        self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lead]:
        """Get all leads for a company by joining through clients and properties."""
        return (
            db.query(self.model)
            .join(self.model.client)
            .filter(self.model.client.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_project_leads(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lead]:
        """Get all leads for a project by joining through properties."""
        return (
            db.query(self.model)
            .join(self.model.property)
            .filter(self.model.property.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


lead = CRUDLead(Lead) 