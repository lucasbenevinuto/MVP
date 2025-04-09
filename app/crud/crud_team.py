from typing import List, Optional, Dict, Any, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.team import Team, UserTeam
from app.schemas.team import TeamCreate, TeamUpdate, UserTeamCreate, UserTeamUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    def get_by_name_and_company(self, db: Session, *, name: str, company_id: int) -> Optional[Team]:
        return db.query(Team).filter(Team.name == name, Team.company_id == company_id).first()
    
    def get_company_teams(self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> List[Team]:
        return db.query(Team).filter(Team.company_id == company_id).offset(skip).limit(limit).all()
    
    def get_manager_teams(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100) -> List[Team]:
        return db.query(Team).filter(Team.manager_id == manager_id).offset(skip).limit(limit).all()


class CRUDUserTeam(CRUDBase[UserTeam, UserTeamCreate, UserTeamUpdate]):
    def get_team_members(self, db: Session, *, team_id: int, skip: int = 0, limit: int = 100) -> List[UserTeam]:
        return db.query(UserTeam).filter(UserTeam.team_id == team_id).offset(skip).limit(limit).all()
    
    def get_user_teams(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[UserTeam]:
        return db.query(UserTeam).filter(UserTeam.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_by_user_and_team(self, db: Session, *, user_id: int, team_id: int) -> Optional[UserTeam]:
        return db.query(UserTeam).filter(
            UserTeam.user_id == user_id,
            UserTeam.team_id == team_id
        ).first()
    
    def remove_by_user_and_team(self, db: Session, *, user_id: int, team_id: int) -> Optional[UserTeam]:
        obj = self.get_by_user_and_team(db, user_id=user_id, team_id=team_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


team = CRUDTeam(Team)
user_team = CRUDUserTeam(UserTeam) 