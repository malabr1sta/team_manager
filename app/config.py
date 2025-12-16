from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "team_manager"
    database_user: str | None = None
    database_password: str | None = None
    database_name: str | None = None
    database_host: str | None = None
    database_port: int | None = None
    model_config = SettingsConfigDict(env_file="./.env")
