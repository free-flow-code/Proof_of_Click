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
    SEND_CLICKS_PERIOD: int = 3

    ENCRYPTION_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    JWT_TOKEN_DELAY_MINUTES: int = 30
    ORIGINS: list = ["http://127.0.0.1:8000", "http://127.0.0.1:3000"]
    SET_COOKIE_SECURE: bool = False  # Установите True, если используете HTTPS

    REDIS_CLUSTER_HOST: str = "localhost"
    REDIS_CLUSTER_PORT: int = 7000

    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_PORT: int

    MAX_BLOCKS: int
    REDIS_NODE_TAG_1: str = "{group1}"
    REDIS_NODE_TAG_2: str = "{group2}"
    REDIS_NODE_TAG_3: str = "{group3}"
    START_INIT_FUNCS: bool = True


settings = Settings()
