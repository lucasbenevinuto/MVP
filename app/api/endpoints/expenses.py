from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
from datetime import datetime

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Expense])
def read_expenses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve expenses.
    """
    if crud.user.is_superuser(current_user):
        expenses = crud.expense.get_multi(db, skip=skip, limit=limit)
    else:
        # Get expenses for the current user's company
        expenses = crud.expense.get_company_expenses(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return expenses


@router.post("/", response_model=schemas.Expense)
async def create_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_in: schemas.ExpenseCreate,
    receipt: UploadFile = File(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new expense.
    """
    # Verify project exists
    project = crud.project.get(db, id=expense_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to create expense for this project
    if not crud.user.is_superuser(current_user) and current_user.company_id != project.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # If property_id is provided, verify it exists and belongs to the project
    if expense_in.property_id:
        property = crud.property.get(db, id=expense_in.property_id)
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        if property.project_id != expense_in.project_id:
            raise HTTPException(status_code=400, detail="Property does not belong to the specified project")
    
    # Handle receipt file if provided
    receipt_path = None
    if receipt:
        # Save file to disk
        file_type = receipt.content_type
        filename = receipt.filename
        
        # Create directory if it doesn't exist
        year = datetime.now().year
        month = datetime.now().month
        upload_dir = f"./uploads/expenses/{year}/{month:02d}/{project.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        receipt_path = f"{upload_dir}/{filename}"
        with open(receipt_path, "wb") as f:
            content = await receipt.read()
            f.write(content)
        
        # Update expense_in with receipt path
        expense_in.receipt_path = receipt_path
    
    # Add created_by_id
    expense_in.created_by_id = current_user.id
    
    expense = crud.expense.create(db, obj_in=expense_in)
    return expense


@router.get("/{expense_id}", response_model=schemas.Expense)
def read_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get expense by ID.
    """
    expense = crud.expense.get(db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Get the project to check company
    project = crud.project.get(db, id=expense.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this expense
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return expense


@router.put("/{expense_id}", response_model=schemas.Expense)
async def update_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    expense_in: schemas.ExpenseUpdate,
    receipt: UploadFile = File(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an expense.
    """
    expense = crud.expense.get(db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Get the project to check company
    project = crud.project.get(db, id=expense.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this expense
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # If changing project, verify new project exists and user has permission
    if expense_in.project_id and expense_in.project_id != expense.project_id:
        new_project = crud.project.get(db, id=expense_in.project_id)
        if not new_project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not crud.user.is_superuser(current_user) and new_project.company_id != current_user.company_id:
            raise HTTPException(status_code=400, detail="Not enough permissions for the new project")
    
    # If changing property, verify it exists and belongs to the project
    if expense_in.property_id and expense_in.property_id != expense.property_id:
        property = crud.property.get(db, id=expense_in.property_id)
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Get the right project_id for comparison (either the new one or the old one)
        project_id_to_check = expense_in.project_id if expense_in.project_id else expense.project_id
        if property.project_id != project_id_to_check:
            raise HTTPException(status_code=400, detail="Property does not belong to the specified project")
    
    # Handle receipt file if provided
    if receipt:
        # Delete old receipt if it exists
        if expense.receipt_path and os.path.exists(expense.receipt_path):
            try:
                os.remove(expense.receipt_path)
            except Exception as e:
                # Log error but continue
                print(f"Error removing old receipt: {e}")
        
        # Save new file
        file_type = receipt.content_type
        filename = receipt.filename
        
        # Create directory if it doesn't exist
        project_id = expense_in.project_id if expense_in.project_id else expense.project_id
        year = datetime.now().year
        month = datetime.now().month
        upload_dir = f"./uploads/expenses/{year}/{month:02d}/{project_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        receipt_path = f"{upload_dir}/{filename}"
        with open(receipt_path, "wb") as f:
            content = await receipt.read()
            f.write(content)
        
        # Update expense_in with new receipt path
        expense_in.receipt_path = receipt_path
    
    expense = crud.expense.update(db, db_obj=expense, obj_in=expense_in)
    return expense


@router.delete("/{expense_id}", response_model=schemas.Expense)
def delete_expense(
    *,
    db: Session = Depends(deps.get_db),
    expense_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an expense.
    """
    expense = crud.expense.get(db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Get the project to check company
    project = crud.project.get(db, id=expense.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to delete this expense
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Delete receipt file if it exists
    if expense.receipt_path and os.path.exists(expense.receipt_path):
        try:
            os.remove(expense.receipt_path)
        except Exception as e:
            # Log error but continue with DB deletion
            print(f"Error deleting receipt file: {e}")
    
    expense = crud.expense.remove(db, id=expense_id)
    return expense


@router.get("/project/{project_id}/", response_model=List[schemas.Expense])
def read_project_expenses(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve expenses for a specific project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to access this project
    if not crud.user.is_superuser(current_user) and project.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    expenses = crud.expense.get_project_expenses(db, project_id=project_id, skip=skip, limit=limit)
    return expenses


@router.get("/property/{property_id}/", response_model=List[schemas.Expense])
def read_property_expenses(
    *,
    db: Session = Depends(deps.get_db),
    property_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve expenses for a specific property.
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
    
    expenses = crud.expense.get_property_expenses(db, property_id=property_id, skip=skip, limit=limit)
    return expenses 