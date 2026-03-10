from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # AI Provider
    AI_PROVIDER: str = Field(default="groq")
    GROQ_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="")
    CLAUDE_MODEL: str = Field(default="claude-sonnet-4-6")

    # SauceDemo
    SAUCEDEMO_URL: str = Field(default="https://www.saucedemo.com")

    # App auth
    PLATFORM_USERNAME: str = Field(default="admin")
    PLATFORM_PASSWORD: str = Field(default="demo1234")

    # Settings
    HEADLESS_BROWSER: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
