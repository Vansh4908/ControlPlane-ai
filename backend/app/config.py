import os
from dotenv import load_dotenv

load_dotenv()


raw_db_uri = os.getenv(
    "DATABASE_URL",
    "sqlite:///controlplane.db"
)

if raw_db_uri and raw_db_uri.startswith("postgres://"):
    raw_db_uri = raw_db_uri.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = raw_db_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")