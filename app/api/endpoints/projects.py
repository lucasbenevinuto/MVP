from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Project])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve projects.
    """
    if crud.user.is_superuser(current_user):
        projects = crud.project.get_multi(db, skip=skip, limit=limit)
    else:
        # Get projects for the current user's company
        projects = crud.project.get_company_projects(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return projects


@router.post("/", response_model=schemas.Project)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: schemas.ProjectCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new project.
    """
    print("\n📥 [POST] Novo projeto recebido")
    print("📄 Payload:", project_in.dict())
    print("👤 Usuário autenticado:", current_user.email, "| ID:", current_user.id)

    # Check if user has permission to create project for this company
    if not crud.user.is_superuser(current_user) and current_user.company_id != project_in.company_id:
        print("⛔ Permissão negada para a empresa:", project_in.company_id)
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Check if project with same name already exists in company
    project = crud.project.get_by_name_and_company(db, name=project_in.name, company_id=project_in.company_id)
    if project:
        print("⚠️ Projeto já existe:", project.name)
        raise HTTPException(
            status_code=400,
            detail="The project with this name already exists in the company.",
        )
    
    # Verify manager exists
    manager = crud.user.get(db, id=project_in.manager_id)
    if not manager:
        print("❌ Gerente não encontrado com ID:", project_in.manager_id)
        raise HTTPException(status_code=404, detail="Manager not found")
    if manager.company_id != project_in.company_id:
        print("❌ Empresa do gerente diferente da empresa do projeto.")
        raise HTTPException(status_code=400, detail="Manager must belong to the same company")
    
    project = crud.project.create(db, obj_in=project_in)
    print("✅ Projeto criado com sucesso:", project.name)
    return project



@router.get("/{project_id}", response_model=schemas.Project)
def read_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get project by ID.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return project


@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    project_in: schemas.ProjectUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a project.
    """

    print("\n🛠 Dados recebidos no PUT:")
    print(project_in.dict())
    
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # If changing manager, verify new manager exists
    if project_in.manager_id and project_in.manager_id != project.manager_id:
        manager = crud.user.get(db, id=project_in.manager_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        if manager.company_id != project.company_id:
            raise HTTPException(status_code=400, detail="Manager must belong to the same company")
    
    project = crud.project.update(db, db_obj=project, obj_in=project_in)
    return project


@router.delete("/{project_id}", response_model=schemas.Project)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to delete this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    project = crud.project.remove(db, id=project_id)
    return project


@router.get("/{project_id}/teams/", response_model=List[schemas.TeamProject])
def read_project_teams(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve teams assigned to a specific project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    teams = crud.team_project.get_project_teams(db, project_id=project_id, skip=skip, limit=limit)
    return teams


@router.post("/{project_id}/teams/", response_model=schemas.TeamProject)
def assign_team_to_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    team_project_in: schemas.TeamProjectCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Assign a team to a project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Verify team exists and belongs to same company
    team = crud.team.get(db, id=team_project_in.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.company_id != project.company_id:
        raise HTTPException(status_code=400, detail="Team and project must belong to same company")
    
    # Check if team is already assigned
    existing_assignment = crud.team_project.get_by_team_and_project(
        db, team_id=team_project_in.team_id, project_id=project_id
    )
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Team is already assigned to this project")
    
    team_project = crud.team_project.create(db, obj_in=team_project_in)
    return team_project


@router.delete("/{project_id}/teams/{team_id}", response_model=schemas.TeamProject)
def remove_team_from_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    team_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove a team from a project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Get team assignment
    team_assignment = crud.team_project.get_by_team_and_project(db, team_id=team_id, project_id=project_id)
    if not team_assignment:
        raise HTTPException(status_code=404, detail="Team is not assigned to this project")
    
    removed_assignment = crud.team_project.remove_by_team_and_project(db, team_id=team_id, project_id=project_id)
    return removed_assignment


@router.get("/{project_id}/tasks/", response_model=List[schemas.ProjectTask])
def read_project_tasks(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve tasks for a specific project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    tasks = crud.project_task.get_project_tasks(db, project_id=project_id, skip=skip, limit=limit)
    return tasks


@router.post("/{project_id}/tasks/", response_model=schemas.ProjectTask)
def create_project_task(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    task_in: schemas.ProjectTaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new task for a project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # If task has assignee, verify assignee exists
    if task_in.assignee_id:
        assignee = crud.user.get(db, id=task_in.assignee_id)
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
        if assignee.company_id != project.company_id:
            raise HTTPException(status_code=400, detail="Assignee must belong to the same company")
    
    task = crud.project_task.create(db, obj_in=task_in)
    return task


@router.put("/{project_id}/tasks/{task_id}", response_model=schemas.ProjectTask)
def update_project_task(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    task_id: int,
    task_in: schemas.ProjectTaskUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a project task.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    task = crud.project_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.project_id != project_id:
        raise HTTPException(status_code=400, detail="Task does not belong to this project")
    
    # If changing assignee, verify assignee exists
    if task_in.assignee_id and task_in.assignee_id != task.assignee_id:
        assignee = crud.user.get(db, id=task_in.assignee_id)
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
        if assignee.company_id != project.company_id:
            raise HTTPException(status_code=400, detail="Assignee must belong to the same company")
    
    task = crud.project_task.update(db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/{project_id}/tasks/{task_id}", response_model=schemas.ProjectTask)
def delete_project_task(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    task_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a project task.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    task = crud.project_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.project_id != project_id:
        raise HTTPException(status_code=400, detail="Task does not belong to this project")
    
    task = crud.project_task.remove(db, id=task_id)
    return task


@router.get("/{project_id}/updates/", response_model=List[schemas.ProjectUpdate])
def read_project_updates(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve updates for a specific project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    updates = crud.project_update.get_project_updates(db, project_id=project_id, skip=skip, limit=limit)
    return updates


@router.post("/{project_id}/updates/", response_model=schemas.ProjectUpdate)
def create_project_update(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    update_in: schemas.ProjectUpdateCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new update for a project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Make sure the update is for the right project
    if update_in.project_id != project_id:
        raise HTTPException(status_code=400, detail="Update must be for this project")
    
    # Set current user as author if not specified
    if not update_in.user_id:
        update_in.user_id = current_user.id
    
    update = crud.project_update.create(db, obj_in=update_in)
    return update 