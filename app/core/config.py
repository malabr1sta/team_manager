from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str | None = None
    database_user: str | None = None
    database_password: str | None = None
    database_name: str | None = None
    database_host: str | None = None
    database_port: int | None = None
    test: bool | None = None
    secret_key: str = ""
    model_config = SettingsConfigDict(env_file="././.env")

    @property
    def use_schema(self) -> bool:
        """Use database schema
        (False for SQLite in tests, True for PostgreSQL in prod)"""
        return not self.test
