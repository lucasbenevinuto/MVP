from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/summary", response_model=Dict[str, Any])
def get_dashboard_summary(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get summary metrics for dashboard.
    """
    # Define scope based on user permissions
    if crud.user.is_superuser(current_user):
        company_id = None  # All companies for superuser
    else:
        company_id = current_user.company_id
    
    # Get counts
    counts = {}
    
    # Get projects count
    if company_id:
        projects = crud.project.get_company_projects(db, company_id=company_id)
        counts["projects"] = len(projects)
        
        # Get properties count by status
        properties = []
        for project in projects:
            project_properties = crud.property.get_project_properties(db, project_id=project.id)
            properties.extend(project_properties)
        
        property_status_counts = {}
        for prop in properties:
            status = prop.status
            if status in property_status_counts:
                property_status_counts[status] += 1
            else:
                property_status_counts[status] = 1
        
        counts["properties"] = len(properties)
        counts["property_status"] = property_status_counts
        
        # Get leads count by status
        leads = crud.lead.get_company_leads(db, company_id=company_id)
        
        lead_status_counts = {}
        for lead in leads:
            status = lead.status
            if status in lead_status_counts:
                lead_status_counts[status] += 1
            else:
                lead_status_counts[status] = 1
        
        counts["leads"] = len(leads)
        counts["lead_status"] = lead_status_counts
        
        # Get contracts count by status
        contracts = crud.contract.get_company_contracts(db, company_id=company_id)
        
        contract_status_counts = {}
        for contract in contracts:
            status = contract.status
            if status in contract_status_counts:
                contract_status_counts[status] += 1
            else:
                contract_status_counts[status] = 1
        
        counts["contracts"] = len(contracts)
        counts["contract_status"] = contract_status_counts
        
        # Calculate total expenses
        total_expenses = 0
        for project in projects:
            project_expenses = crud.expense.get_expenses_sum_by_project(db, project_id=project.id)
            total_expenses += project_expenses
        
        counts["total_expenses"] = total_expenses
        
        # Get expenses by category
        expense_by_category = {}
        for project in projects:
            for category in schemas.ExpenseCategoryEnum:
                category_expenses = crud.expense.get_expenses_sum_by_category(
                    db, project_id=project.id, category=category
                )
                if category in expense_by_category:
                    expense_by_category[category] += category_expenses
                else:
                    expense_by_category[category] = category_expenses
        
        counts["expense_by_category"] = expense_by_category
    else:
        # Superuser - get global stats
        counts["projects"] = db.query(func.count(models.Project.id)).scalar()
        counts["properties"] = db.query(func.count(models.Property.id)).scalar()
        counts["leads"] = db.query(func.count(models.Lead.id)).scalar()
        counts["contracts"] = db.query(func.count(models.Contract.id)).scalar()
        
        # Get property status counts
        property_status_counts = {}
        for status in schemas.PropertyStatusEnum:
            count = db.query(func.count(models.Property.id)).filter(
                models.Property.status == status
            ).scalar()
            property_status_counts[status] = count
        counts["property_status"] = property_status_counts
        
        # Get lead status counts
        lead_status_counts = {}
        for status in schemas.LeadStatusEnum:
            count = db.query(func.count(models.Lead.id)).filter(
                models.Lead.status == status
            ).scalar()
            lead_status_counts[status] = count
        counts["lead_status"] = lead_status_counts
        
        # Get contract status counts
        contract_status_counts = {}
        for status in schemas.ContractStatusEnum:
            count = db.query(func.count(models.Contract.id)).filter(
                models.Contract.status == status
            ).scalar()
            contract_status_counts[status] = count
        counts["contract_status"] = contract_status_counts
        
        # Calculate total expenses
        total_expenses = db.query(func.sum(models.Expense.amount)).scalar() or 0
        counts["total_expenses"] = total_expenses
        
        # Get expenses by category
        expense_by_category = {}
        for category in schemas.ExpenseCategoryEnum:
            category_expenses = db.query(func.sum(models.Expense.amount)).filter(
                models.Expense.category == category
            ).scalar() or 0
            expense_by_category[category] = category_expenses
        counts["expense_by_category"] = expense_by_category
    
    return counts


@router.get("/recent_activities", response_model=Dict[str, List])
def get_recent_activities(
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get recent activities for dashboard.
    """
    # Define scope based on user permissions
    if crud.user.is_superuser(current_user):
        company_id = None  # All companies for superuser
    else:
        company_id = current_user.company_id
    
    recent = {}
    
    # Get recent leads
    if company_id:
        # Get recent leads for company
        leads_query = (
            db.query(models.Lead)
            .join(models.Lead.client)
            .filter(models.Client.company_id == company_id)
            .order_by(models.Lead.created_at.desc())
            .limit(limit)
        )
    else:
        # Get all recent leads for superuser
        leads_query = (
            db.query(models.Lead)
            .order_by(models.Lead.created_at.desc())
            .limit(limit)
        )
    
    recent_leads = leads_query.all()
    recent["leads"] = [schemas.Lead.from_orm(lead) for lead in recent_leads]
    
    # Get recent contracts
    if company_id:
        # Complex query to get contracts for company through property->project
        # This is a bit simplified here - in a real app this would be more sophisticated
        recent_contracts = []
        projects = crud.project.get_company_projects(db, company_id=company_id)
        
        for project in projects:
            properties = crud.property.get_project_properties(db, project_id=project.id)
            for prop in properties:
                contracts = crud.contract.get_property_contracts(db, property_id=prop.id, limit=limit)
                recent_contracts.extend(contracts)
        
        # Sort and limit
        recent_contracts.sort(key=lambda x: x.created_at, reverse=True)
        recent_contracts = recent_contracts[:limit]
    else:
        # Get all recent contracts for superuser
        recent_contracts = (
            db.query(models.Contract)
            .order_by(models.Contract.created_at.desc())
            .limit(limit)
            .all()
        )
    
    recent["contracts"] = [schemas.Contract.from_orm(contract) for contract in recent_contracts]
    
    # Get recent expenses
    if company_id:
        # Complex query to get expenses for company through projects
        recent_expenses = []
        projects = crud.project.get_company_projects(db, company_id=company_id)
        
        for project in projects:
            expenses = crud.expense.get_project_expenses(db, project_id=project.id, limit=limit)
            recent_expenses.extend(expenses)
        
        # Sort and limit
        recent_expenses.sort(key=lambda x: x.created_at, reverse=True)
        recent_expenses = recent_expenses[:limit]
    else:
        # Get all recent expenses for superuser
        recent_expenses = (
            db.query(models.Expense)
            .order_by(models.Expense.created_at.desc())
            .limit(limit)
            .all()
        )
    
    recent["expenses"] = [schemas.Expense.from_orm(expense) for expense in recent_expenses]
    
    return recent


@router.get("/active_projects", response_model=List[schemas.Project])
def get_active_projects(
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get active projects for dashboard.
    """
    # Define scope based on user permissions
    if crud.user.is_superuser(current_user):
        # Get active projects for superuser
        projects = (
            db.query(models.Project)
            .filter(models.Project.status == "in_progress")
            .order_by(models.Project.updated_at.desc())
            .limit(limit)
            .all()
        )
    else:
        # Get active projects for user's company
        projects = (
            db.query(models.Project)
            .filter(
                models.Project.company_id == current_user.company_id,
                models.Project.status == "in_progress"
            )
            .order_by(models.Project.updated_at.desc())
            .limit(limit)
            .all()
        )
    
    return projects 