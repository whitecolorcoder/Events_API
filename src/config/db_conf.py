from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = Field(alias="POSTGRES_HOST")
    DB_PASS: str = Field(alias="POSTGRES_PASSWORD")
    DB_USER: str = Field(alias="POSTGRES_USERNAME")
    DB_PORT: int = Field(alias="POSTGRES_PORT")
    DB_NAME: str = Field(alias="POSTGRES_DATABASE_NAME")

    EVENTS_API_KEY: str | None = None

    @property
    def DATABASE_URL(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", populate_by_name=True)


settings = Settings()
