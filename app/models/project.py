from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, Date, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"  # Planejamento
    IN_PROGRESS = "in_progress"  # Em execução
    ON_HOLD = "on_hold"  # Paralisado
    COMPLETED = "completed"  # Concluído
    CANCELLED = "cancelled"  # Cancelado


class Project(BaseModel):
    """Modelo de projeto imobiliário"""
    
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    total_area = Column(Float)  # Área total em m²
    budget = Column(Float)  # Orçamento
    start_date = Column(Date)
    expected_end_date = Column(Date)
    actual_end_date = Column(Date)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relacionamentos
    company = relationship("Company", back_populates="projects")
    manager = relationship("User", back_populates="managed_projects")
    teams = relationship("TeamProject", back_populates="project", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")
    updates = relationship("ProjectUpdate", back_populates="project", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="project", cascade="all, delete-orphan")


class TeamProject(BaseModel):
    """Associação entre equipes e projetos"""
    
    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    
    # Relacionamentos
    team = relationship("Team", back_populates="projects")
    project = relationship("Project", back_populates="teams")


class ProjectTask(BaseModel):
    """Tarefas de projeto"""
    
    title = Column(String, nullable=False)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="pending")  # pending, in_progress, completed
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    # Relacionamentos
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User")


class ProjectUpdate(BaseModel):
    """Atualizações do projeto"""
    
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relacionamentos
    project = relationship("Project", back_populates="updates")
    user = relationship("User") 