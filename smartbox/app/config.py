from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Smart IP Box MVP"
    api_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8080
    db_path: str = "./data/smartbox.db"
    admin_username: str = "admin"
    admin_password: str = "admin"
    fernet_key: str = ""

    class Config:
        env_prefix = "SMARTBOX_"
        extra = "ignore"


class DeviceSettingUpdate(BaseModel):
    key: str
    value: str


settings = Settings()
