from typing import Optional, List
from datetime import date
from pydantic import BaseModel
from enum import Enum


class ContractTypeEnum(str, Enum):
    SALE = "sale"  # Venda
    RENTAL = "rental"  # Locação
    LEASE = "lease"  # Arrendamento
    OTHER = "other"  # Outro


class ContractStatusEnum(str, Enum):
    ACTIVE = "active"  # Ativo
    PENDING = "pending"  # Pendente
    EXPIRED = "expired"  # Vencido
    CANCELLED = "cancelled"  # Cancelado
    COMPLETED = "completed"  # Finalizado


# Shared properties
class ContractBase(BaseModel):
    contract_number: str
    type: ContractTypeEnum
    description: Optional[str] = None
    client_id: int
    property_id: int
    signing_date: date
    expiration_date: Optional[date] = None
    contract_value: float
    status: Optional[ContractStatusEnum] = None
    notes: Optional[str] = None


# Properties to receive on contract creation
class ContractCreate(ContractBase):
    pass


# Properties to receive on contract update
class ContractUpdate(BaseModel):
    contract_number: Optional[str] = None
    type: Optional[ContractTypeEnum] = None
    description: Optional[str] = None
    client_id: Optional[int] = None
    property_id: Optional[int] = None
    signing_date: Optional[date] = None
    expiration_date: Optional[date] = None
    contract_value: Optional[float] = None
    status: Optional[ContractStatusEnum] = None
    notes: Optional[str] = None


# Shared properties for contract document
class ContractDocumentBase(BaseModel):
    filename: str
    description: Optional[str] = None
    file_type: Optional[str] = None
    file_path: str
    contract_id: int


# Properties to receive on contract document creation
class ContractDocumentCreate(ContractDocumentBase):
    pass


# Properties to receive on contract document update
class ContractDocumentUpdate(BaseModel):
    filename: Optional[str] = None
    description: Optional[str] = None
    file_type: Optional[str] = None
    file_path: Optional[str] = None


# Properties to return to client
class ContractDocument(ContractDocumentBase):
    id: int
    
    class Config:
        from_attributes = True


# Properties to return to client
class Contract(ContractBase):
    id: int
    documents: List[ContractDocument] = []
    
    class Config:
        from_attributes = True 