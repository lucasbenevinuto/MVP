from pydantic import BaseModel
from typing import Optional, List


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    company_id: int
    manager_id: int


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[int] = None
    manager_id: Optional[int] = None


class TeamInDBBase(TeamBase):
    id: int
    
    class Config:
        from_attributes = True


class Team(TeamInDBBase):
    pass


class UserTeamBase(BaseModel):
    user_id: int
    team_id: int
    role: str


class UserTeamCreate(UserTeamBase):
    pass


class UserTeamUpdate(BaseModel):
    role: Optional[str] = None


class UserTeamInDBBase(UserTeamBase):
    id: int
    
    class Config:
        from_attributes = True


class UserTeam(UserTeamInDBBase):
    pass 