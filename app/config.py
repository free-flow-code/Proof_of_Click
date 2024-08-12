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

    BACKEND_DOMAIN: str = "http://127.0.0.1:8000"
    FRONTEND_DOMAIN: str = "http://127.0.0.1:3000"
    ENCRYPTION_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    JWT_TOKEN_DELAY_MINUTES: int = 30
    ORIGINS: list = ["http://127.0.0.1:8000", "http://127.0.0.1:3000"]
    SET_COOKIE_SECURE: bool = False  # Установите True, если используете HTTPS

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_PORT: int

    MAX_BLOCKS: int


settings = Settings()
