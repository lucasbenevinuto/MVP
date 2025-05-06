from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Client])
def read_clients(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve clients.
    """
    if crud.user.is_superuser(current_user):
        clients = crud.client.get_multi(db, skip=skip, limit=limit)
    else:
        # Get clients for the current user's company
        clients = crud.client.get_company_clients(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return clients


@router.post("/", response_model=schemas.Client)
def create_client(
    *,
    db: Session = Depends(deps.get_db),
    client_in: schemas.ClientCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new client.
    """
    # Check if user has permission to create client for this company
    if not crud.user.is_superuser(current_user) and current_user.company_id != client_in.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Check if client with same document already exists
    client = crud.client.get_by_document(db, document=client_in.document)
    if client:
        raise HTTPException(
            status_code=400,
            detail="The client with this document already exists in the system.",
        )
    
    client = crud.client.create(db, obj_in=client_in)
    return client


@router.get("/{client_id}", response_model=schemas.Client)
def read_client(
    *,
    db: Session = Depends(deps.get_db),
    client_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get client by ID.
    """
    client = crud.client.get(db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if user has permission to access this client
    if not crud.user.is_superuser(current_user) and client.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return client


@router.put("/{client_id}", response_model=schemas.Client)
def update_client(
    *,
    db: Session = Depends(deps.get_db),
    client_id: int,
    client_in: schemas.ClientUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a client.
    """
    client = crud.client.get(db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if user has permission to update this client
    if not crud.user.is_superuser(current_user) and client.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Check if updating to a document that already exists
    if client_in.document and client_in.document != client.document:
        existing_client = crud.client.get_by_document(db, document=client_in.document)
        if existing_client and existing_client.id != client_id:
            raise HTTPException(
                status_code=400,
                detail="The client with this document already exists in the system.",
            )
    
    client = crud.client.update(db, db_obj=client, obj_in=client_in)
    return client


@router.delete("/{client_id}", response_model=schemas.Client)
def delete_client(
    *,
    db: Session = Depends(deps.get_db),
    client_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a client.
    """
    client = crud.client.get(db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if user has permission to delete this client
    if not crud.user.is_superuser(current_user) and client.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Check if client has any leads or contracts
    leads = crud.lead.get_client_leads(db, client_id=client_id)
    if leads:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete client with associated leads. Delete the leads first.",
        )
    
    contracts = crud.contract.get_client_contracts(db, client_id=client_id)
    if contracts:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete client with associated contracts. Delete the contracts first.",
        )
    
    client = crud.client.remove(db, id=client_id)
    return client


@router.get("/{client_id}/leads/", response_model=List[schemas.Lead])
def read_client_leads(
    *,
    db: Session = Depends(deps.get_db),
    client_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve leads for a specific client.
    """
    client = crud.client.get(db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if user has permission to access this client
    if not crud.user.is_superuser(current_user) and client.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    leads = crud.lead.get_client_leads(db, client_id=client_id, skip=skip, limit=limit)
    return leads 