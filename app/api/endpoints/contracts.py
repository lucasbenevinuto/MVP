from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
from datetime import datetime

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Contract])
def read_contracts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve contracts.
    """
    if crud.user.is_superuser(current_user):
        contracts = crud.contract.get_multi(db, skip=skip, limit=limit)
    else:
        # Get contracts for the current user's company
        contracts = crud.contract.get_company_contracts(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return contracts


@router.post("/", response_model=schemas.Contract)
def create_contract(
    *,
    db: Session = Depends(deps.get_db),
    contract_in: schemas.ContractCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new contract.
    """
    # Verify property exists
    property = crud.property.get(db, id=contract_in.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get the project for this property to check company
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to create contract for this property/company
    if not crud.user.is_superuser(current_user) and current_user.company_id != project.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Verify client exists
    client = crud.client.get(db, id=contract_in.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if client belongs to the same company
    if client.company_id != project.company_id:
        raise HTTPException(status_code=400, detail="Client and property must belong to the same company")
    
    # Check if contract with the same number already exists
    existing_contract = crud.contract.get_by_contract_number(db, contract_number=contract_in.contract_number)
    if existing_contract:
        raise HTTPException(
            status_code=400,
            detail="A contract with this number already exists.",
        )
    
    contract = crud.contract.create(db, obj_in=contract_in)
    return contract


@router.get("/{contract_id}", response_model=schemas.Contract)
def read_contract(
    *,
    db: Session = Depends(deps.get_db),
    contract_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get contract by ID.
    """
    contract = crud.contract.get(db, id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Get the property and project to check company
    property = crud.property.get(db, id=contract.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Associated property not found")
    
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Associated project not found")
    
    # Check if user has permission to access this contract
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return contract


@router.put("/{contract_id}", response_model=schemas.Contract)
def update_contract(
    *,
    db: Session = Depends(deps.get_db),
    contract_id: int,
    contract_in: schemas.ContractUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a contract.
    """
    contract = crud.contract.get(db, id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Get the property and project to check company
    property = crud.property.get(db, id=contract.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Associated property not found")
    
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Associated project not found")
    
    # Check if user has permission to update this contract
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # If changing property, verify new property exists and user has permission
    if contract_in.property_id and contract_in.property_id != contract.property_id:
        new_property = crud.property.get(db, id=contract_in.property_id)
        if not new_property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        new_project = crud.project.get(db, id=new_property.project_id)
        if not new_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not crud.user.is_superuser(current_user) and new_project.company_id != current_user.company_id:
            raise HTTPException(status_code=400, detail="Not enough permissions for the new property")
    
    # If changing client, verify new client exists and belongs to the same company
    if contract_in.client_id and contract_in.client_id != contract.client_id:
        new_client = crud.client.get(db, id=contract_in.client_id)
        if not new_client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        if new_client.company_id != project.company_id:
            raise HTTPException(status_code=400, detail="Client must belong to the same company")
    
    contract = crud.contract.update(db, db_obj=contract, obj_in=contract_in)
    return contract


@router.delete("/{contract_id}", response_model=schemas.Contract)
def delete_contract(
    *,
    db: Session = Depends(deps.get_db),
    contract_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a contract.
    """
    contract = crud.contract.get(db, id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Get the property and project to check company
    property = crud.property.get(db, id=contract.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Associated property not found")
    
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Associated project not found")
    
    # Check if user has permission to delete this contract
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    contract = crud.contract.remove(db, id=contract_id)
    return contract


@router.get("/{contract_id}/documents", response_model=List[schemas.ContractDocument])
def read_contract_documents(
    *,
    db: Session = Depends(deps.get_db),
    contract_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get documents for a contract.
    """
    contract = crud.contract.get(db, id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Get the property and project to check company
    property = crud.property.get(db, id=contract.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Associated property not found")
    
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Associated project not found")
    
    # Check if user has permission to access this contract
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    documents = crud.contract_document.get_contract_documents(db, contract_id=contract_id)
    return documents


@router.post("/{contract_id}/documents", response_model=schemas.ContractDocument)
async def create_contract_document(
    *,
    db: Session = Depends(deps.get_db),
    contract_id: int,
    description: str = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a document for a contract.
    """
    contract = crud.contract.get(db, id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Get the property and project to check company
    property = crud.property.get(db, id=contract.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Associated property not found")
    
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Associated project not found")
    
    # Check if user has permission to add documents to this contract
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Save file to disk
    file_type = file.content_type
    filename = file.filename
    
    # Create directory if it doesn't exist
    year = datetime.now().year
    month = datetime.now().month
    upload_dir = f"./uploads/contracts/{year}/{month:02d}/{contract_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = f"{upload_dir}/{filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create document in the database
    document_in = schemas.ContractDocumentCreate(
        filename=filename,
        description=description,
        file_type=file_type,
        file_path=file_path,
        contract_id=contract_id
    )
    
    document = crud.contract_document.create(db, obj_in=document_in)
    return document


@router.delete("/{contract_id}/documents/{document_id}", response_model=schemas.ContractDocument)
def delete_contract_document(
    *,
    db: Session = Depends(deps.get_db),
    contract_id: int,
    document_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a contract document.
    """
    contract = crud.contract.get(db, id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Get the property and project to check company
    property = crud.property.get(db, id=contract.property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Associated property not found")
    
    project = crud.project.get(db, id=property.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Associated project not found")
    
    # Check if user has permission to delete documents from this contract
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    document = crud.contract_document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.contract_id != contract_id:
        raise HTTPException(status_code=400, detail="Document does not belong to this contract")
    
    # Delete file from disk
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        # Log the error but continue - we still want to remove from DB
        print(f"Error deleting file: {e}")
    
    document = crud.contract_document.remove(db, id=document_id)
    return document 