from typing import List, Optional
from pydantic import BaseModel, Field


class RequirementSchema(BaseModel):
    title: str = Field(..., description="Short requirement title")
    description: str = Field(..., description="Full requirement description")
    feature: str = Field(default="General", description="Feature area (e.g. Login, Cart)")
    priority: str = Field(default="Medium", description="High / Medium / Low")
    acceptance_criteria: str = Field(default="", description="Acceptance criteria text")
    test_types: str = Field(default="Functional", description="Comma-separated test types")
    actors: List[str] = Field(default_factory=list, description="Actors / users involved")
    actions: List[str] = Field(default_factory=list, description="Actions performed")
    expected_outputs: List[str] = Field(default_factory=list, description="Expected outcomes")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Valid Login",
                "description": "Users can log in with correct credentials",
                "feature": "Login",
                "priority": "High",
                "acceptance_criteria": "User lands on products page",
                "test_types": "Functional,Smoke",
                "actors": ["standard_user"],
                "actions": ["enter username", "enter password", "click login"],
                "expected_outputs": ["products page displayed"],
            }
        }
