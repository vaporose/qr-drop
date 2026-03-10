from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_file=".env")
    host_ip: str = "localhost"
    port: int = 5173
    protocol: str = "http"
    base_url: str = f"{protocol}://{host_ip}:{port}"
    base_chat_url: str = f"{base_url}/chat/"


SETTINGS = Settings()

