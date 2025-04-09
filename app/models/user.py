from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """Modelo de usuário do sistema"""
    
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    
    # Relacionamentos
    company = relationship("Company", back_populates="users")
    teams = relationship("UserTeam", back_populates="user", cascade="all, delete-orphan")
    managed_teams = relationship("Team", back_populates="manager", cascade="all, delete-orphan")
    managed_projects = relationship("Project", back_populates="manager", cascade="all, delete-orphan") 