from typing import Optional, List
from datetime import date
from pydantic import BaseModel
from enum import Enum


class ClientTypeEnum(str, Enum):
    INDIVIDUAL = "individual"  # Pessoa Física
    COMPANY = "company"  # Pessoa Jurídica


class LeadStatusEnum(str, Enum):
    INITIAL_CONTACT = "initial_contact"  # Contato inicial
    PROPERTY_VISIT = "property_visit"  # Visita ao imóvel
    NEGOTIATION = "negotiation"  # Em negociação
    PROPOSAL = "proposal"  # Proposta feita
    CONTRACT = "contract"  # Contrato assinado
    CLOSED = "closed"  # Fechado/Concluído
    LOST = "lost"  # Perdido


# Shared properties for client
class ClientBase(BaseModel):
    name: str
    client_type: ClientTypeEnum
    document: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    notes: Optional[str] = None
    company_id: int


# Properties to receive on client creation
class ClientCreate(ClientBase):
    pass


# Properties to receive on client update
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    client_type: Optional[ClientTypeEnum] = None
    document: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    notes: Optional[str] = None


# Shared properties for lead
class LeadBase(BaseModel):
    property_id: int
    client_id: int
    status: Optional[LeadStatusEnum] = None
    first_contact_date: Optional[date] = None
    last_contact_date: Optional[date] = None
    next_contact_date: Optional[date] = None
    visit_date: Optional[date] = None
    interest_level: Optional[int] = None
    budget: Optional[float] = None
    notes: Optional[str] = None
    assigned_user_id: Optional[int] = None


# Properties to receive on lead creation
class LeadCreate(LeadBase):
    pass


# Properties to receive on lead update
class LeadUpdate(BaseModel):
    status: Optional[LeadStatusEnum] = None
    first_contact_date: Optional[date] = None
    last_contact_date: Optional[date] = None
    next_contact_date: Optional[date] = None
    visit_date: Optional[date] = None
    interest_level: Optional[int] = None
    budget: Optional[float] = None
    notes: Optional[str] = None
    assigned_user_id: Optional[int] = None


# Properties to return to client
class Lead(LeadBase):
    id: int
    
    class Config:
        from_attributes = True


# Properties to return to client
class Client(ClientBase):
    id: int
    leads: List[Lead] = []
    
    class Config:
        from_attributes = True 