import os
from functools import cached_property

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    version: str = "0.1.0"
    log_level: str = "INFO"
    cors_origins: list[str] = ["https://localhost:30011"]

    # Database
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "architect"
    db_user: str = "architect"

    # Secrets directory (K8s mounted secrets)
    secrets_dir: str = os.environ.get("SECRETS_DIR", "/app/secrets")

    # Output directory for rendered artifacts
    output_dir: str = "/app/data/outputs"

    @cached_property
    def db_password(self) -> str:
        secret_path = os.path.join(self.secrets_dir, "postgres_password")
        try:
            return open(secret_path).read().strip()
        except FileNotFoundError:
            return "architect-dev"

    @cached_property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
