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
    R2_ENDPOINT_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    AWS_CUSTOM_DOMAIN: str

enviroment = Settings()

