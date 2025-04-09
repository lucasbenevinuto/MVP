from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from enum import Enum


class PropertyTypeEnum(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    COMMERCIAL = "commercial"
    LAND = "land"
    INDUSTRIAL = "industrial"


class PropertyStatusEnum(str, Enum):
    PLANNING = "planning"
    FOUNDATION = "foundation"
    STRUCTURE = "structure"
    FINISHING = "finishing"
    COMPLETED = "completed"
    SOLD = "sold"


class PropertyBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: PropertyTypeEnum
    status: Optional[PropertyStatusEnum] = PropertyStatusEnum.PLANNING
    address: Optional[str] = None
    unit_number: Optional[str] = None
    floor: Optional[int] = None
    area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    garage_spots: Optional[int] = None
    price: Optional[float] = None
    construction_cost: Optional[float] = None
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    is_sold: Optional[bool] = False
    sale_date: Optional[date] = None
    sale_price: Optional[float] = None
    project_id: int


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[PropertyTypeEnum] = None
    status: Optional[PropertyStatusEnum] = None
    address: Optional[str] = None
    unit_number: Optional[str] = None
    floor: Optional[int] = None
    area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    garage_spots: Optional[int] = None
    price: Optional[float] = None
    construction_cost: Optional[float] = None
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    is_sold: Optional[bool] = None
    sale_date: Optional[date] = None
    sale_price: Optional[float] = None
    project_id: Optional[int] = None


class PropertyInDBBase(PropertyBase):
    id: int
    
    class Config:
        from_attributes = True


class Property(PropertyInDBBase):
    pass


class PropertyUpdateBase(BaseModel):
    title: str
    content: str
    status: Optional[PropertyStatusEnum] = None
    property_id: int
    user_id: int


class PropertyUpdateCreate(PropertyUpdateBase):
    pass


class PropertyUpdateUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[PropertyStatusEnum] = None


class PropertyUpdateInDBBase(PropertyUpdateBase):
    id: int
    
    class Config:
        from_attributes = True


class PropertyUpdate(PropertyUpdateInDBBase):
    pass 