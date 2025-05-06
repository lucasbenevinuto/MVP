from typing import Optional
from datetime import date
from pydantic import BaseModel
from enum import Enum


class ExpenseCategoryEnum(str, Enum):
    MATERIALS = "materials"  # Materiais
    LABOR = "labor"  # Mão de obra
    TAXES = "taxes"  # Impostos
    PERMITS = "permits"  # Licenças/Alvarás
    SERVICES = "services"  # Serviços
    EQUIPMENT = "equipment"  # Equipamentos
    UTILITIES = "utilities"  # Serviços básicos (água, luz)
    MARKETING = "marketing"  # Marketing
    ADMINISTRATIVE = "administrative"  # Administrativo
    OTHER = "other"  # Outros


# Shared properties
class ExpenseBase(BaseModel):
    description: str
    category: ExpenseCategoryEnum
    amount: float
    date: date
    project_id: int
    property_id: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_document: Optional[str] = None
    supplier_contact: Optional[str] = None
    receipt_path: Optional[str] = None
    receipt_description: Optional[str] = None
    notes: Optional[str] = None


# Properties to receive on expense creation
class ExpenseCreate(ExpenseBase):
    created_by_id: Optional[int] = None  # Will be set from the current user


# Properties to receive on expense update
class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[ExpenseCategoryEnum] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    project_id: Optional[int] = None
    property_id: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_document: Optional[str] = None
    supplier_contact: Optional[str] = None
    receipt_path: Optional[str] = None
    receipt_description: Optional[str] = None
    notes: Optional[str] = None


# Properties to return to client
class Expense(ExpenseBase):
    id: int
    created_by_id: int
    
    class Config:
        from_attributes = True 