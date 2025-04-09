from pydantic import BaseModel
from typing import Optional, List


class CompanyBase(BaseModel):
    name: str
    document: str
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    document: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyInDBBase(CompanyBase):
    id: int
    
    class Config:
        from_attributes = True


class Company(CompanyInDBBase):
    pass 