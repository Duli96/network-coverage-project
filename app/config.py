from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv


load_dotenv()

user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
host = os.environ["POSTGRES_HOST"]
database = os.environ["POSTGRES_DB"]
port = os.environ["POSTGRES_PORT"]


@dataclass
class Config:
    HTTPS: bool = False
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{user}:{password}@{host}:{port}/{database}"
    )
    PROXY_WMS: bool = False
    SCRIPT_NAME: str = "api"
    JWT_SIGNING_ALGORITHM: str = "ES256"
    GEOSERVER_TIMEOUT: int = 20
    LOG_LEVEL: str = "INFO"
    CONFIG_PATH: Optional[str] = None
    # Timeout on acquiring connections from the connection pool
    DB_POOL_TIMEOUT: Optional[int] = None
