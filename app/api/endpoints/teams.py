from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Team])
def read_teams(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve teams.
    """
    if crud.user.is_superuser(current_user):
        teams = crud.team.get_multi(db, skip=skip, limit=limit)
    else:
        # Get teams for the current user's company
        teams = crud.team.get_company_teams(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return teams


@router.post("/", response_model=schemas.Team)
def create_team(
    *,
    db: Session = Depends(deps.get_db),
    team_in: schemas.TeamCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new team.
    """
    # Check if user has permission to create team for this company
    if not crud.user.is_superuser(current_user) and current_user.company_id != team_in.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Check if team with same name already exists in company
    team = crud.team.get_by_name_and_company(db, name=team_in.name, company_id=team_in.company_id)
    if team:
        raise HTTPException(
            status_code=400,
            detail="The team with this name already exists in the company.",
        )
    
    # Verify manager exists
    manager = crud.user.get(db, id=team_in.manager_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    team = crud.team.create(db, obj_in=team_in)
    return team


@router.get("/{team_id}", response_model=schemas.Team)
def read_team(
    *,
    db: Session = Depends(deps.get_db),
    team_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get team by ID.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user has permission to access this team
    if not crud.user.is_superuser(current_user) and team.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return team


@router.put("/{team_id}", response_model=schemas.Team)
def update_team(
    *,
    db: Session = Depends(deps.get_db),
    team_id: int,
    team_in: schemas.TeamUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user has permission to update this team
    if not crud.user.is_superuser(current_user) and team.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # If changing manager, verify new manager exists
    if team_in.manager_id and team_in.manager_id != team.manager_id:
        manager = crud.user.get(db, id=team_in.manager_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
    
    team = crud.team.update(db, db_obj=team, obj_in=team_in)
    return team


@router.delete("/{team_id}", response_model=schemas.Team)
def delete_team(
    *,
    db: Session = Depends(deps.get_db),
    team_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user has permission to delete this team
    if not crud.user.is_superuser(current_user) and team.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Rely on SQLAlchemy cascade to handle related records
    team = crud.team.remove(db, id=team_id)
    return team


@router.get("/{team_id}/members/", response_model=List[schemas.UserTeam])
def read_team_members(
    *,
    db: Session = Depends(deps.get_db),
    team_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve members for a specific team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user has permission to access this team
    if not crud.user.is_superuser(current_user) and team.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    members = crud.user_team.get_team_members(db, team_id=team_id, skip=skip, limit=limit)
    return members


@router.post("/{team_id}/members/", response_model=schemas.UserTeam)
def add_team_member(
    *,
    db: Session = Depends(deps.get_db),
    team_id: int,
    user_team_in: schemas.UserTeamCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add member to a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user has permission to update this team
    if not crud.user.is_superuser(current_user) and team.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Verify user exists and belongs to same company
    user = crud.user.get(db, id=user_team_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.company_id != team.company_id:
        raise HTTPException(status_code=400, detail="User and team must belong to same company")
    
    # Check if user is already a member
    existing_membership = crud.user_team.get_by_user_and_team(
        db, user_id=user_team_in.user_id, team_id=team_id
    )
    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a member of this team")
    
    user_team = crud.user_team.create(db, obj_in=user_team_in)
    return user_team


@router.delete("/{team_id}/members/{user_id}", response_model=schemas.UserTeam)
def remove_team_member(
    *,
    db: Session = Depends(deps.get_db),
    team_id: int,
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove member from a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user has permission to update this team
    if not crud.user.is_superuser(current_user) and team.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Get membership
    membership = crud.user_team.get_by_user_and_team(db, user_id=user_id, team_id=team_id)
    if not membership:
        raise HTTPException(status_code=404, detail="User is not a member of this team")
    
    # Cannot remove manager from team
    if team.manager_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot remove team manager from team")
    
    removed_membership = crud.user_team.remove_by_user_and_team(db, user_id=user_id, team_id=team_id)
    return removed_membership 