from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Definimos las variables y su tipo
    db_connection_url: str = ""

    # JWT SECTION
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Email confirmation token
    EMAIL_TOKEN_EXPIRE_HOURS: int = 24

    # Email/SMTP
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAILS_FROM: str

    FRONTEND_URL: str

    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Instanciamos para usar en el proyecto
settings = Settings()