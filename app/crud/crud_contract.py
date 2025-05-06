from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractUpdate


class CRUDContract(CRUDBase[Contract, ContractCreate, ContractUpdate]):
    def get_by_contract_number(self, db: Session, *, contract_number: str) -> Optional[Contract]:
        return db.query(self.model).filter(self.model.contract_number == contract_number).first()
    
    def get_company_contracts(
        self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Contract]:
        """Get all contracts for a company by joining through properties and projects."""
        return (
            db.query(self.model)
            .join(self.model.property)
            .join(self.model.property.project)
            .filter(self.model.property.project.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_client_contracts(
        self, db: Session, *, client_id: int, skip: int = 0, limit: int = 100
    ) -> List[Contract]:
        """Get all contracts for a client."""
        return (
            db.query(self.model)
            .filter(self.model.client_id == client_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_property_contracts(
        self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100
    ) -> List[Contract]:
        """Get all contracts for a property."""
        return (
            db.query(self.model)
            .filter(self.model.property_id == property_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


contract = CRUDContract(Contract) 