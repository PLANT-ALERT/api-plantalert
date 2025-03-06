from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_PORT: int
    DB_DATABASE: str
    SECRET: str
    INFLUXDB_URL: str
    INFLUXDB_TOKEN: str
    INFLUXDB_ORG: str
    NATIVENOTIFY_FIRST: str
    NATIVENOTIFY_SECOND: str

enviroment = Settings()

