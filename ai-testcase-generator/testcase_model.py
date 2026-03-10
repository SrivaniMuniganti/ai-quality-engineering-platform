from typing import List, Optional
from pydantic import BaseModel, Field


class TestCaseModel(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., description="Short test case title")
    steps: List[str] = Field(default_factory=list, description="Step-by-step test actions")
    expected_result: str = Field(default="", description="Expected outcome")
    priority: str = Field(default="Medium", description="High / Medium / Low")
    risk_level: str = Field(default="Medium", description="High / Medium / Low")
    test_type: str = Field(default="Functional", description="Functional / Negative / E2E / etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TC-001",
                "title": "Verify valid login redirects to products page",
                "steps": [
                    "Navigate to https://www.saucedemo.com",
                    "Enter 'standard_user' in username field",
                    "Enter 'secret_sauce' in password field",
                    "Click the Login button",
                ],
                "expected_result": "Products inventory page is displayed",
                "priority": "High",
                "risk_level": "High",
                "test_type": "Functional",
            }
        }
