from pydantic_settings import BaseSettings

# see .env file for required environment variables
class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    UPLOAD_DIR: str = "data/uploads"
    FAISS_INDEX_DIR: str = "data/faiss_index"

    class Config:
        env_file = ".env"


settings = Settings() #type: ignore
