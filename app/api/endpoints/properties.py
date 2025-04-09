from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Property])
def read_properties(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve properties.
    """
    # Superuser can see all properties
    if crud.user.is_superuser(current_user):
        properties = crud.property.get_multi(db, skip=skip, limit=limit)
        return properties
    
    # Non-superuser can only see properties from projects in their company
    if current_user.company_id:
        # Get all projects for the user's company
        projects = crud.project.get_company_projects(db, company_id=current_user.company_id)
        project_ids = [project.id for project in projects]
        
        if not project_ids:
            return []
        
        # Get properties for these projects - need to handle this manually since
        # we're filtering on multiple project IDs
        properties = []
        for project_id in project_ids:
            project_properties = crud.property.get_project_properties(
                db, project_id=project_id, skip=skip, limit=limit
            )
            properties.extend(project_properties)
        return properties[:limit]
    
    return []


@router.post("/", response_model=schemas.Property)
def create_property(
    *,
    db: Session = Depends(deps.get_db),
    property_in: schemas.PropertyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new property.
    """
    # Verify project exists
    project = crud.project.get(db, id=property_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to create property for this project
    if not crud.user.is_superuser(current_user) and current_user.company_id != project.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Check if property with same name already exists in project
    existing_property = crud.property.get_by_name_and_project(
        db, name=property_in.name, project_id=property_in.project_id
    )
    if existing_property:
        raise HTTPException(
            status_code=400,
            detail="The property with this name already exists in the project.",
        )
    
    property = crud.property.create(db, obj_in=property_in)
    return property


@router.get("/{property_id}", response_model=schemas.Property)
def read_property(
    *,
    db: Session = Depends(deps.get_db),
    property_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get property by ID.
    """
    property = crud.property.get(db, id=property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get the project for this property
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this property
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return property


@router.put("/{property_id}", response_model=schemas.Property)
def update_property(
    *,
    db: Session = Depends(deps.get_db),
    property_id: int,
    property_in: schemas.PropertyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a property.
    """
    property = crud.property.get(db, id=property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get the project for this property
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this property
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # If changing project, verify new project exists and user has permission
    if property_in.project_id and property_in.project_id != property.project_id:
        new_project = crud.project.get(db, id=property_in.project_id)
        if not new_project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not crud.user.is_superuser(current_user) and new_project.company_id != current_user.company_id:
            raise HTTPException(status_code=400, detail="Not enough permissions for the new project")
    
    property = crud.property.update(db, db_obj=property, obj_in=property_in)
    return property


@router.delete("/{property_id}", response_model=schemas.Property)
def delete_property(
    *,
    db: Session = Depends(deps.get_db),
    property_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a property.
    """
    property = crud.property.get(db, id=property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get the project for this property
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to delete this property
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    property = crud.property.remove(db, id=property_id)
    return property


@router.get("/project/{project_id}/", response_model=List[schemas.Property])
def read_project_properties(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve properties for a specific project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    properties = crud.property.get_project_properties(db, project_id=project_id, skip=skip, limit=limit)
    return properties


@router.get("/status/{status}/", response_model=List[schemas.Property])
def read_properties_by_status(
    *,
    db: Session = Depends(deps.get_db),
    status: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve properties by status.
    """
    # Validate status
    try:
        status_enum = schemas.PropertyStatusEnum(status)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join([s.value for s in schemas.PropertyStatusEnum])}"
        )
    
    # Get properties by status
    properties = crud.property.get_by_status(db, status=status_enum, skip=skip, limit=limit)
    
    # Filter out properties the user doesn't have permission to access
    if not crud.user.is_superuser(current_user):
        # Get all projects for the user's company
        projects = crud.project.get_company_projects(db, company_id=current_user.company_id)
        project_ids = [project.id for project in projects]
        
        # Filter properties
        properties = [p for p in properties if p.project_id in project_ids]
    
    return properties


@router.get("/{property_id}/updates/", response_model=List[schemas.PropertyUpdate])
def read_property_updates(
    *,
    db: Session = Depends(deps.get_db),
    property_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve updates for a specific property.
    """
    property = crud.property.get(db, id=property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get the project for this property
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this property
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    updates = crud.property_update.get_property_updates(db, property_id=property_id, skip=skip, limit=limit)
    return updates


@router.post("/{property_id}/updates/", response_model=schemas.PropertyUpdate)
def create_property_update(
    *,
    db: Session = Depends(deps.get_db),
    property_id: int,
    update_in: schemas.PropertyUpdateCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new update for a property.
    """
    property = crud.property.get(db, id=property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get the project for this property
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this property
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Make sure the update is for the right property
    if update_in.property_id != property_id:
        raise HTTPException(status_code=400, detail="Update must be for this property")
    
    # Set current user as author if not specified
    if not update_in.user_id:
        update_in.user_id = current_user.id
    
    update = crud.property_update.create(db, obj_in=update_in)
    return update 