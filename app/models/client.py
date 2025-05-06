from sqlalchemy import Column, String, Text, ForeignKey, Integer, Date, Enum, Boolean, Float
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class ClientType(str, enum.Enum):
    INDIVIDUAL = "individual"  # Pessoa Física
    COMPANY = "company"  # Pessoa Jurídica


class LeadStatus(str, enum.Enum):
    INITIAL_CONTACT = "initial_contact"  # Contato inicial
    PROPERTY_VISIT = "property_visit"  # Visita ao imóvel
    NEGOTIATION = "negotiation"  # Em negociação
    PROPOSAL = "proposal"  # Proposta feita
    CONTRACT = "contract"  # Contrato assinado
    CLOSED = "closed"  # Fechado/Concluído
    LOST = "lost"  # Perdido


class Client(BaseModel):
    """Modelo de cliente"""
    
    name = Column(String, index=True, nullable=False)
    client_type = Column(Enum(ClientType), nullable=False)
    document = Column(String, index=True, nullable=False)  # CPF ou CNPJ
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    notes = Column(Text)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    
    # Relacionamentos
    company = relationship("Company", back_populates="clients")
    contracts = relationship("Contract", back_populates="client")
    leads = relationship("Lead", back_populates="client")


class Lead(BaseModel):
    """Modelo de lead/prospecção"""
    
    property_id = Column(Integer, ForeignKey("property.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    status = Column(Enum(LeadStatus), default=LeadStatus.INITIAL_CONTACT)
    
    # Datas de acompanhamento
    first_contact_date = Column(Date)
    last_contact_date = Column(Date)
    next_contact_date = Column(Date)
    visit_date = Column(Date)
    
    # Informações adicionais
    interest_level = Column(Integer)  # 1-5 para nível de interesse
    budget = Column(Float)  # Orçamento do cliente
    notes = Column(Text)
    
    # Responsável pelo lead
    assigned_user_id = Column(Integer, ForeignKey("user.id"))
    
    # Relacionamentos
    property = relationship("Property", back_populates="leads")
    client = relationship("Client", back_populates="leads")
    assigned_user = relationship("User", back_populates="assigned_leads") 