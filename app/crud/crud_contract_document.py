from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.contract import ContractDocument
from app.schemas.contract import ContractDocumentCreate, ContractDocumentUpdate


class CRUDContractDocument(CRUDBase[ContractDocument, ContractDocumentCreate, ContractDocumentUpdate]):
    def get_contract_documents(
        self, db: Session, *, contract_id: int, skip: int = 0, limit: int = 100
    ) -> List[ContractDocument]:
        """Get all documents for a contract."""
        return (
            db.query(self.model)
            .filter(self.model.contract_id == contract_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


contract_document = CRUDContractDocument(ContractDocument) 