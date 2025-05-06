from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, Date, Enum, Boolean
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class PropertyType(str, enum.Enum):
    APARTMENT = "apartment"  # Apartamento
    HOUSE = "house"  # Casa
    COMMERCIAL = "commercial"  # Comercial
    LAND = "land"  # Terreno
    INDUSTRIAL = "industrial"  # Industrial


class PropertyStatus(str, enum.Enum):
    PLANNING = "planning"  # Planejamento
    FOUNDATION = "foundation"  # Fundação
    STRUCTURE = "structure"  # Estrutura
    FINISHING = "finishing"  # Acabamento
    COMPLETED = "completed"  # Concluído
    SOLD = "sold"  # Vendido


class Property(BaseModel):
    """Modelo de imóvel/propriedade"""
    
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    type = Column(Enum(PropertyType), nullable=False)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.PLANNING)
    address = Column(String)
    unit_number = Column(String)  # Número da unidade
    floor = Column(Integer)  # Andar
    area = Column(Float)  # Área em m²
    bedrooms = Column(Integer)  # Número de quartos
    bathrooms = Column(Integer)  # Número de banheiros
    garage_spots = Column(Integer)  # Vagas de garagem
    price = Column(Float)  # Preço
    construction_cost = Column(Float)  # Custo de construção
    start_date = Column(Date)
    expected_completion_date = Column(Date)
    actual_completion_date = Column(Date)
    is_sold = Column(Boolean, default=False)
    sale_date = Column(Date)
    sale_price = Column(Float)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    
    # Relacionamentos
    project = relationship("Project", back_populates="properties")
    updates = relationship("PropertyUpdate", back_populates="property", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="property", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="property", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="property", cascade="all, delete-orphan")


class PropertyUpdate(BaseModel):
    """Atualizações do imóvel"""
    
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(PropertyStatus))
    property_id = Column(Integer, ForeignKey("property.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relacionamentos
    property = relationship("Property", back_populates="updates")
    user = relationship("User") 