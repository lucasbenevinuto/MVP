from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Company(BaseModel):
    """Modelo de empresa/construtora"""
    
    name = Column(String, index=True, nullable=False)
    document = Column(String, unique=True, index=True, nullable=False)  # CNPJ
    address = Column(String)
    phone = Column(String)
    description = Column(Text)
    logo_url = Column(String)
    
    # Relacionamentos
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="company", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="company", cascade="all, delete-orphan") 