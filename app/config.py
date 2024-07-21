from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore"
    )

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "root"
    DB_NAME: str = "mydb"

    DOMAIN: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    JWT_TOKEN_DELAY_MINUTES: int = 30
    ORIGINS: list = ["localhost:8000", "127.0.0.1:8000", "localhost:3000", "http://127.0.0.1:3000"]

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    #SMTP_HOST: str
    #SMTP_USER: str
    #SMTP_PASSWORD: str
    #SMTP_PORT: int


settings = Settings()
