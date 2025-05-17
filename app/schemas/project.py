from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List, Union
from datetime import date
from enum import Enum


class ProjectStatusEnum(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    total_area: Optional[float] = None
    budget: Optional[float] = None
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[ProjectStatusEnum] = ProjectStatusEnum.PLANNING
    company_id: int
    manager_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    total_area: Optional[float] = None
    budget: Optional[float] = None
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[ProjectStatusEnum] = None
    company_id: Optional[int] = None
    manager_id: Optional[int] = None

    @validator('start_date', 'expected_end_date', 'actual_end_date', pre=True)
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value


class ProjectInDBBase(ProjectBase):
    id: int
    
    class Config:
        from_attributes = True


class Project(ProjectInDBBase):
    pass


class TeamProjectBase(BaseModel):
    team_id: int
    project_id: int


class TeamProjectCreate(TeamProjectBase):
    pass


class TeamProjectInDBBase(TeamProjectBase):
    id: int
    
    class Config:
        from_attributes = True


class TeamProject(TeamProjectInDBBase):
    pass


class ProjectTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "pending"
    project_id: int
    assignee_id: Optional[int] = None


class ProjectTaskCreate(ProjectTaskBase):
    pass


class ProjectTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None


class ProjectTaskInDBBase(ProjectTaskBase):
    id: int
    
    class Config:
        from_attributes = True


class ProjectTask(ProjectTaskInDBBase):
    pass


class ProjectUpdateBase(BaseModel):
    title: str
    content: str
    project_id: int
    user_id: int


class ProjectUpdateCreate(ProjectUpdateBase):
    pass


class ProjectUpdateUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class ProjectUpdateInDBBase(ProjectUpdateBase):
    id: int
    
    class Config:
        from_attributes = True


class ProjectUpdate(ProjectUpdateInDBBase):
    pass 