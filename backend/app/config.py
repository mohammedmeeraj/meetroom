from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str 

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 1000

    model_config = SettingsConfigDict(env_file=".env")
     
