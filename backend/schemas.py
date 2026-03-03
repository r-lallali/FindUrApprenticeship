"""Pydantic schemas for the alternance dashboard API."""

import json
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ── Offers ──────────────────────────────────────────────

class OfferCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    department: Optional[str] = None
    contract_type: Optional[str] = None
    salary: Optional[str] = None
    salary_min: Optional[str] = None
    salary_max: Optional[str] = None
    description: Optional[str] = None
    profile: Optional[str] = None
    category: Optional[str] = None
    skills_languages: Optional[str] = None
    skills_frameworks: Optional[str] = None
    skills_tools: Optional[str] = None
    skills_certifications: Optional[str] = None
    skills_methodologies: Optional[str] = None
    skills_all: Optional[str] = None
    publication_date: Optional[datetime] = None
    source: str
    url: Optional[str] = None
    source_id: Optional[str] = None
    is_school: bool = False
    is_alternance: bool = True


class OfferResponse(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    department: Optional[str] = None
    contract_type: Optional[str] = None
    salary: Optional[str] = None
    salary_min: Optional[str] = None
    salary_max: Optional[str] = None
    description: Optional[str] = None
    profile: Optional[str] = None
    category: Optional[str] = None
    skills_languages: Optional[List[str]] = None
    skills_frameworks: Optional[List[str]] = None
    skills_tools: Optional[List[str]] = None
    skills_certifications: Optional[List[str]] = None
    skills_methodologies: Optional[List[str]] = None
    skills_all: Optional[List[str]] = None
    publication_date: Optional[datetime] = None
    source: str
    url: Optional[str] = None
    source_id: Optional[str] = None
    is_school: bool = False
    is_alternance: bool = True
    scraped_at: Optional[datetime] = None

    # Populated dynamically when user is authenticated
    favorite_status: Optional[str] = None  # to_apply | applied | rejected | None
    favorite_id: Optional[str] = None

    model_config = {"from_attributes": True}

    @field_validator(
        'skills_languages', 'skills_frameworks', 'skills_tools',
        'skills_certifications', 'skills_methodologies', 'skills_all',
        mode='before'
    )
    @classmethod
    def parse_json_list(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class OfferListResponse(BaseModel):
    offers: List[OfferResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class FilterOptions(BaseModel):
    categories: List[str] = []
    locations: List[str] = []
    departments: List[str] = []
    contract_types: List[str] = []
    profiles: List[str] = []
    sources: List[str] = []
    technologies: List[str] = []


class ScrapingStatus(BaseModel):
    source: str
    status: str
    offers_found: int = 0
    offers_new: int = 0
    message: str = ""


class TechStats(BaseModel):
    top_languages: List[dict] = []
    top_frameworks: List[dict] = []
    top_tools: List[dict] = []
    top_certifications: List[dict] = []
    top_methodologies: List[dict] = []
    total_it_offers: int = 0
    total_offers: int = 0
    top_departments: List[dict] = []
    top_companies: List[dict] = []
    top_categories: List[dict] = []


# ── Auth ────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Favorites ───────────────────────────────────────────

class FavoriteCreate(BaseModel):
    offer_id: str
    status: str = "to_apply"
    notes: Optional[str] = None


class FavoriteUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class FavoriteResponse(BaseModel):
    id: str
    offer_id: str
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    offer: Optional[OfferResponse] = None
    model_config = {"from_attributes": True}
