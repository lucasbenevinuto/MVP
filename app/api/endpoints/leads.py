from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import date

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Lead])
def read_leads(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve leads.
    """
    if crud.user.is_superuser(current_user):
        leads = crud.lead.get_multi(db, skip=skip, limit=limit)
    else:
        # Get leads for the current user's company
        leads = crud.lead.get_company_leads(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return leads


@router.post("/", response_model=schemas.Lead)
def create_lead(
    *,
    db: Session = Depends(deps.get_db),
    client_id: int = Form(...),
    property_id: int = Form(...),
    status: schemas.LeadStatusEnum = Form(...),
    first_contact_date: Optional[date] = Form(None),
    last_contact_date: Optional[date] = Form(None),
    next_contact_date: Optional[date] = Form(None),
    visit_date: Optional[date] = Form(None),
    interest_level: Optional[int] = Form(None),
    budget: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    assigned_user_id: Optional[int] = Form(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new lead.
    """
    # Create lead_in object from form fields
    lead_in = schemas.LeadCreate(
        client_id=client_id,
        property_id=property_id,
        status=status,
        first_contact_date=first_contact_date,
        last_contact_date=last_contact_date,
        next_contact_date=next_contact_date,
        visit_date=visit_date,
        interest_level=interest_level,
        budget=budget,
        notes=notes,
        assigned_user_id=assigned_user_id,
    )

    # Verify property exists
    property = crud.property.get(db, id=lead_in.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get the project for this property to check company
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to create lead for this property/company
    if not crud.user.is_superuser(current_user) and current_user.company_id != project.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Verify client exists
    client = crud.client.get(db, id=lead_in.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if client belongs to the same company
    if client.company_id != project.company_id:
        raise HTTPException(status_code=400, detail="Client and property must belong to the same company")
    
    # If assigned_user_id is provided, verify user exists and belongs to the company
    if lead_in.assigned_user_id:
        user = crud.user.get(db, id=lead_in.assigned_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Assigned user not found")
        if user.company_id != project.company_id:
            raise HTTPException(status_code=400, detail="Assigned user must belong to the same company")
    else:
        # Assign to current user by default
        lead_in.assigned_user_id = current_user.id
    
    # Set first_contact_date to today if not provided
    if not lead_in.first_contact_date:
        lead_in.first_contact_date = date.today()
    
    # Set last_contact_date to today if not provided
    if not lead_in.last_contact_date:
        lead_in.last_contact_date = date.today()
    
    lead = crud.lead.create(db, obj_in=lead_in)
    return lead


@router.get("/{lead_id}", response_model=schemas.Lead)
def read_lead(
    *,
    db: Session = Depends(deps.get_db),
    lead_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get lead by ID.
    """
    lead = crud.lead.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get the client to check company
    client = crud.client.get(db, id=lead.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Associated client not found")
    
    # Check if user has permission to access this lead
    if not crud.user.is_superuser(current_user) and client.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return lead


@router.put("/{lead_id}", response_model=schemas.Lead)
def update_lead(
    *,
    db: Session = Depends(deps.get_db),
    lead_id: int,
    status: Optional[schemas.LeadStatusEnum] = Form(None),
    first_contact_date: Optional[date] = Form(None),
    last_contact_date: Optional[date] = Form(None),
    next_contact_date: Optional[date] = Form(None),
    visit_date: Optional[date] = Form(None),
    interest_level: Optional[int] = Form(None),
    budget: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    assigned_user_id: Optional[int] = Form(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a lead.
    """
    lead = crud.lead.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get the client to check company
    client = crud.client.get(db, id=lead.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Associated client not found")
    
    # Check if user has permission to update this lead
    if not crud.user.is_superuser(current_user) and client.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Create lead_in object from form fields
    lead_in = schemas.LeadUpdate(
        status=status,
        first_contact_date=first_contact_date,
        last_contact_date=last_contact_date,
        next_contact_date=next_contact_date,
        visit_date=visit_date,
        interest_level=interest_level,
        budget=budget,
        notes=notes,
        assigned_user_id=assigned_user_id,
    )
    
    # If changing assigned user, verify user exists and belongs to the company
    if lead_in.assigned_user_id and lead_in.assigned_user_id != lead.assigned_user_id:
        user = crud.user.get(db, id=lead_in.assigned_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Assigned user not found")
        if user.company_id != client.company_id:
            raise HTTPException(status_code=400, detail="Assigned user must belong to the same company")
    
    # Update last_contact_date if status is changing
    if lead_in.status and lead_in.status != lead.status:
        lead_in.last_contact_date = date.today()
    
    lead = crud.lead.update(db, db_obj=lead, obj_in=lead_in)
    return lead


@router.delete("/{lead_id}", response_model=schemas.Lead)
def delete_lead(
    *,
    db: Session = Depends(deps.get_db),
    lead_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a lead.
    """
    lead = crud.lead.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get the client to check company
    client = crud.client.get(db, id=lead.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Associated client not found")
    
    # Check if user has permission to delete this lead
    if not crud.user.is_superuser(current_user) and client.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    lead = crud.lead.remove(db, id=lead_id)
    return lead


@router.get("/property/{property_id}/", response_model=List[schemas.Lead])
def read_property_leads(
    *,
    db: Session = Depends(deps.get_db),
    property_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve leads for a specific property.
    """
    property = crud.property.get(db, id=property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get the project to check company
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this property
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    leads = crud.lead.get_property_leads(db, property_id=property_id, skip=skip, limit=limit)
    return leads


@router.get("/assigned/{user_id}/", response_model=List[schemas.Lead])
def read_user_assigned_leads(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve leads assigned to a specific user.
    """
    # Check if the target user exists
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions - a user can see their own leads, 
    # or a superuser can see anyone's leads,
    # or a user from the same company can see their colleague's leads
    if (current_user.id != user_id and 
        not crud.user.is_superuser(current_user) and 
        current_user.company_id != user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    leads = crud.lead.get_user_assigned_leads(db, user_id=user_id, skip=skip, limit=limit)
    return leads


@router.get("/status/{status}/", response_model=List[schemas.Lead])
def read_leads_by_status(
    *,
    db: Session = Depends(deps.get_db),
    status: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve leads by status.
    """
    if crud.user.is_superuser(current_user):
        leads = db.query(models.Lead).filter(models.Lead.status == status).offset(skip).limit(limit).all()
    else:
        # Get leads for current user's company with the specified status
        company_leads = crud.lead.get_company_leads(db, company_id=current_user.company_id)
        leads = [lead for lead in company_leads if lead.status == status]
        # Apply pagination
        leads = leads[skip:skip+limit]
    
    return leads 