from sqlalchemy import Column, String, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Team(BaseModel):
    """Modelo de equipe de trabalho"""
    
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relacionamentos
    company = relationship("Company", back_populates="teams")
    manager = relationship("User", back_populates="managed_teams")
    members = relationship("UserTeam", back_populates="team", cascade="all, delete-orphan")
    projects = relationship("TeamProject", back_populates="team", cascade="all, delete-orphan")


class UserTeam(BaseModel):
    """Associação entre usuários e equipes"""
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    role = Column(String, nullable=False)  # Papel do usuário na equipe: Engenheiro, Arquiteto, etc.
    
    # Relacionamentos
    user = relationship("User", back_populates="teams")
    team = relationship("Team", back_populates="members") 