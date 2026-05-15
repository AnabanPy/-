from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class User:
    id: int
    login: str
    full_name: str
    role: str

@dataclass
class Shop:
    id: int
    name: str
    description: str

@dataclass
class FkkoCode:
    id: int
    code_11: str
    name: str
    danger_class: int
    aggregate_state: str
    origin: str

@dataclass
class Batch:
    id: int
    registration_number: str
    registration_date: date
    shop_id: int
    shop_name: str
    fkko_id: int
    fkko_code: str
    fkko_name: str
    danger_class: int
    quantity: float
    unit: str
    operator_name: str
    status: str