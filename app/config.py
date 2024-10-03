from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mysql_user: str
    mysql_password: str
    mysql_db: str
    mysql_host: str
    redis_host: str
    redis_port: int
    bearer_token: str

    class Config:
        env_file = ".env"

settings = Settings()
