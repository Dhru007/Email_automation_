# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     # Database
#     database_url: str

#     # Auth
#     jwt_secret: str
#     jwt_algorithm: str = "HS256"
#     jwt_expire_minutes: int = 1440
#     admin_email: str = "admin@example.com"
#     admin_password: str = "change_me"

#     # Groq
#     groq_api_key: str
#     groq_model: str = "llama-3.3-70b-versatile"
#     groq_temperature: float = 0.5

#     # Embeddings
#     embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

#     # Chroma
#     chroma_mode: str = "persistent"
#     chroma_persist_dir: str = "./chroma_data"
#     chroma_http_host: str = ""
#     chroma_http_port: int = 8000

#     # Gmail
#     google_client_id: str = ""
#     google_client_secret: str = ""
#     google_redirect_uri: str = ""
#     gmail_poll_interval_seconds: int = 60

#     # Misc
#     slack_webhook_url: str = ""
#     frontend_origin: str = "http://localhost:5173"

#     class Config:
#         env_file = "../.env"


# settings = Settings()
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Database
    database_url: str

    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    admin_email: str = "admin@example.com"
    admin_password: str = "D$123"

    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.5

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Chroma
    chroma_mode: str = "persistent"
    chroma_persist_dir: str = "./chroma_data"
    chroma_http_host: str = ""
    chroma_http_port: int = 8000

    # Gmail
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    gmail_poll_interval_seconds: int = 60

    # Misc
    slack_webhook_url: str = ""
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

print("ENV FILE:", BASE_DIR / ".env")
print("DATABASE:", settings.database_url)