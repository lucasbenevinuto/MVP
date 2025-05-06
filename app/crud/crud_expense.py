from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


class CRUDExpense(CRUDBase[Expense, ExpenseCreate, ExpenseUpdate]):
    def get_company_expenses(
        self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Expense]:
        """Get all expenses for a company by joining through projects."""
        return (
            db.query(self.model)
            .join(self.model.project)
            .filter(self.model.project.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_project_expenses(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Expense]:
        """Get all expenses for a project."""
        return (
            db.query(self.model)
            .filter(self.model.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_property_expenses(
        self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100
    ) -> List[Expense]:
        """Get all expenses for a property."""
        return (
            db.query(self.model)
            .filter(self.model.property_id == property_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_expenses_sum_by_project(
        self, db: Session, *, project_id: int
    ) -> float:
        """Get the sum of all expenses for a project."""
        result = db.query(db.func.sum(self.model.amount)).filter(
            self.model.project_id == project_id
        ).scalar()
        return result if result else 0.0
    
    def get_expenses_sum_by_property(
        self, db: Session, *, property_id: int
    ) -> float:
        """Get the sum of all expenses for a property."""
        result = db.query(db.func.sum(self.model.amount)).filter(
            self.model.property_id == property_id
        ).scalar()
        return result if result else 0.0
    
    def get_expenses_sum_by_category(
        self, db: Session, *, project_id: int, category: str
    ) -> float:
        """Get the sum of expenses by category for a project."""
        result = db.query(db.func.sum(self.model.amount)).filter(
            self.model.project_id == project_id,
            self.model.category == category
        ).scalar()
        return result if result else 0.0


expense = CRUDExpense(Expense) 