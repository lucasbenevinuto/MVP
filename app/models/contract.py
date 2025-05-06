from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, Date, Enum, LargeBinary
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class ContractType(str, enum.Enum):
    SALE = "sale"  # Venda
    RENTAL = "rental"  # Locação
    LEASE = "lease"  # Arrendamento
    OTHER = "other"  # Outro


class ContractStatus(str, enum.Enum):
    ACTIVE = "active"  # Ativo
    PENDING = "pending"  # Pendente
    EXPIRED = "expired"  # Vencido
    CANCELLED = "cancelled"  # Cancelado
    COMPLETED = "completed"  # Finalizado


class Contract(BaseModel):
    """Modelo de contrato imobiliário"""
    
    contract_number = Column(String, index=True, nullable=False, unique=True)
    type = Column(Enum(ContractType), nullable=False)
    description = Column(Text)
    
    # Cliente (relacionamento com modelo Client)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    
    # Imóvel relacionado
    property_id = Column(Integer, ForeignKey("property.id"), nullable=False)
    
    # Datas do contrato
    signing_date = Column(Date, nullable=False)
    expiration_date = Column(Date)
    
    # Valores
    contract_value = Column(Float, nullable=False)
    
    # Status
    status = Column(Enum(ContractStatus), default=ContractStatus.PENDING)
    
    # Observações
    notes = Column(Text)
    
    # Relacionamentos
    client = relationship("Client", back_populates="contracts")
    property = relationship("Property", back_populates="contracts")
    documents = relationship("ContractDocument", back_populates="contract", cascade="all, delete-orphan")


class ContractDocument(BaseModel):
    """Documentos anexados ao contrato"""
    
    filename = Column(String, nullable=False)
    description = Column(String)
    file_type = Column(String)  # Tipo MIME do arquivo
    file_path = Column(String)  # Caminho para o arquivo salvo
    contract_id = Column(Integer, ForeignKey("contract.id"), nullable=False)
    
    # Relacionamentos
    contract = relationship("Contract", back_populates="documents") 