"""Configuration settings for Google Search Console MCP Server."""

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    google_credentials_path: str | None = Field(
        default=None,
        description="Path to the Google Cloud credentials file. "
        "If not provided, the GOOGLE_APPLICATION_CREDENTIALS environment variable will be used.",
    )

    google_application_subject: str | None = Field(
        default=None,
        description="Email address to impersonate using domain-wide delegation. "
        "If not provided, the GOOGLE_APPLICATION_SUBJECT environment variable will be used.",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    @property
    def google_credentials(self) -> Path | None:
        """Get the path to the Google Cloud credentials file.

        Returns:
            Path to the credentials file if available.
        """
        if self.google_credentials_path:
            return Path(self.google_credentials_path)

        env_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if env_creds:
            return Path(env_creds)

        return None

    @property
    def subject(self) -> str | None:
        """Get the subject email for domain-wide delegation.

        Returns:
            Subject email address if configured.
        """
        if self.google_application_subject:
            return self.google_application_subject

        return os.environ.get("GOOGLE_APPLICATION_SUBJECT")


def load_settings(**kwargs) -> Settings:
    """Load settings from environment variables."""
    return Settings(**kwargs)
