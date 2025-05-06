from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, Date, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class ExpenseCategory(str, enum.Enum):
    MATERIALS = "materials"  # Materiais
    LABOR = "labor"  # Mão de obra
    TAXES = "taxes"  # Impostos
    PERMITS = "permits"  # Licenças/Alvarás
    SERVICES = "services"  # Serviços
    EQUIPMENT = "equipment"  # Equipamentos
    UTILITIES = "utilities"  # Serviços básicos (água, luz)
    MARKETING = "marketing"  # Marketing
    ADMINISTRATIVE = "administrative"  # Administrativo
    OTHER = "other"  # Outros


class Expense(BaseModel):
    """Modelo de despesa de obra/projeto"""
    
    description = Column(String, nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    
    # Fornecedor (opcional)
    supplier_name = Column(String)
    supplier_document = Column(String)  # CNPJ/CPF
    supplier_contact = Column(String)
    
    # Comprovante
    receipt_path = Column(String)
    receipt_description = Column(String)
    
    # Observações adicionais
    notes = Column(Text)
    
    # Relacionamentos
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("property.id"), nullable=True)  # Opcional, se a despesa for específica de um imóvel
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relacionamentos
    project = relationship("Project", back_populates="expenses")
    property = relationship("Property", back_populates="expenses")
    created_by = relationship("User") 