from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Company])
def read_companies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve companies.
    """
    companies = crud.company.get_multi(db, skip=skip, limit=limit)
    return companies


@router.post("/", response_model=schemas.Company)
def create_company(
    *,
    db: Session = Depends(deps.get_db),
    name: str = Form(...),
    document: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new company.
    """
    # Create company_in object from form fields
    company_in = schemas.CompanyCreate(
        name=name,
        document=document,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
    )

    company = crud.company.get_by_document(db, document=company_in.document)
    if company:
        raise HTTPException(
            status_code=400,
            detail="The company with this document already exists in the system.",
        )
    company = crud.company.create(db, obj_in=company_in)
    return company


@router.get("/{company_id}", response_model=schemas.Company)
def read_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get company by ID.
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=schemas.Company)
def update_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    name: Optional[str] = Form(None),
    document: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a company.
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create company_in object from form fields
    company_in = schemas.CompanyUpdate(
        name=name,
        document=document,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
    )

    company = crud.company.update(db, db_obj=company, obj_in=company_in)
    return company


@router.delete("/{company_id}", response_model=schemas.Company)
def delete_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a company.
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    company = crud.company.remove(db, id=company_id)
    return company


@router.get("/{company_id}/users/", response_model=List[schemas.User])
def read_company_users(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users for a specific company.
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    users = crud.user.get_company_users(db, company_id=company_id, skip=skip, limit=limit)
    return users 