from typing import List, Optional, Dict, Any, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.project import Project, TeamProject, ProjectTask, ProjectUpdate
from app.schemas.project import (
    ProjectCreate, ProjectUpdate as ProjectUpdateSchema,
    TeamProjectCreate, ProjectTaskCreate, ProjectTaskUpdate,
    ProjectUpdateCreate, ProjectUpdateUpdate as ProjectUpdateUpdateSchema
)


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdateSchema]):
    def get_by_name_and_company(self, db: Session, *, name: str, company_id: int) -> Optional[Project]:
        return db.query(Project).filter(Project.name == name, Project.company_id == company_id).first()
    
    def get_company_projects(self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        return db.query(Project).filter(Project.company_id == company_id).offset(skip).limit(limit).all()
    
    def get_manager_projects(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        return db.query(Project).filter(Project.manager_id == manager_id).offset(skip).limit(limit).all()


class CRUDTeamProject(CRUDBase[TeamProject, TeamProjectCreate, TeamProjectCreate]):
    def get_project_teams(self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100) -> List[TeamProject]:
        return db.query(TeamProject).filter(TeamProject.project_id == project_id).offset(skip).limit(limit).all()
    
    def get_team_projects(self, db: Session, *, team_id: int, skip: int = 0, limit: int = 100) -> List[TeamProject]:
        return db.query(TeamProject).filter(TeamProject.team_id == team_id).offset(skip).limit(limit).all()
    
    def get_by_team_and_project(self, db: Session, *, team_id: int, project_id: int) -> Optional[TeamProject]:
        return db.query(TeamProject).filter(
            TeamProject.team_id == team_id,
            TeamProject.project_id == project_id
        ).first()
    
    def remove_by_team_and_project(self, db: Session, *, team_id: int, project_id: int) -> Optional[TeamProject]:
        obj = self.get_by_team_and_project(db, team_id=team_id, project_id=project_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


class CRUDProjectTask(CRUDBase[ProjectTask, ProjectTaskCreate, ProjectTaskUpdate]):
    def get_project_tasks(self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100) -> List[ProjectTask]:
        return db.query(ProjectTask).filter(ProjectTask.project_id == project_id).offset(skip).limit(limit).all()
    
    def get_user_tasks(self, db: Session, *, assignee_id: int, skip: int = 0, limit: int = 100) -> List[ProjectTask]:
        return db.query(ProjectTask).filter(ProjectTask.assignee_id == assignee_id).offset(skip).limit(limit).all()


class CRUDProjectUpdate(CRUDBase[ProjectUpdate, ProjectUpdateCreate, ProjectUpdateUpdateSchema]):
    def get_project_updates(self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100) -> List[ProjectUpdate]:
        return db.query(ProjectUpdate).filter(ProjectUpdate.project_id == project_id).offset(skip).limit(limit).all()
    
    def get_user_updates(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[ProjectUpdate]:
        return db.query(ProjectUpdate).filter(ProjectUpdate.user_id == user_id).offset(skip).limit(limit).all()


project = CRUDProject(Project)
team_project = CRUDTeamProject(TeamProject)
project_task = CRUDProjectTask(ProjectTask)
project_update = CRUDProjectUpdate(ProjectUpdate) 