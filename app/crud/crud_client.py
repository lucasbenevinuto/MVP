from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    def get_by_document(self, db: Session, *, document: str) -> Optional[Client]:
        return db.query(self.model).filter(self.model.document == document).first()
    
    def get_company_clients(
        self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Client]:
        """Get all clients for a company."""
        return (
            db.query(self.model)
            .filter(self.model.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


client = CRUDClient(Client) 