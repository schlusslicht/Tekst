import os

from functools import lru_cache
from secrets import token_hex
from urllib.parse import quote

from pydantic import BaseSettings, EmailStr, Field, HttpUrl, conint, validator

from tekst import pkg_meta
from tekst.models.common import ModelBase
from tekst.utils.strings import safe_name


def _select_env_files() -> list[str]:
    """
    Selects the dotenv (.env) files to load.
    Values from these files override the default
    values used in the config model classes.

    Selection and priority work as follows:

    - A maximum of two env files will be loaded (".env" and a second one)
    - Additional env files override values found in ".env"
    - If one additional env file is found, selection is complete

    Selection steps:

    1. ".env" if it exists
    2. Custom env file defined in "TEKST_ENV_FILE" env var if it exists
    3. ".env.dev" if it exists AND if TEKST_DEV_MODE env var is set to true

    :return: List of .env file paths
    :rtype: list[str]
    """
    env_files = []
    # define used env file names
    f_env = ".env"
    f_env_dev = ".env.dev"
    f_env_custom = os.environ.get("TEKST_ENV_FILE")
    # prio logic
    if os.path.exists(f_env):
        env_files.append(f_env)
    if f_env_custom and os.path.exists(f_env_custom):
        env_files.append(f_env_custom)
    elif os.environ.get("TEKST_DEV_MODE") and os.path.exists(f_env_dev):
        env_files.append(f_env_dev)
    return env_files


class DbConfig(ModelBase):
    """Database config model"""

    protocol: str = "mongodb"
    host: str = "127.0.0.1"
    port: int = 27017
    user: str = "root"
    password: str = "root"
    name: str = "tekst"

    @validator("host", "password", pre=True)
    def url_quote(cls, v) -> str:
        return quote(str(v).encode("utf8"), safe="")

    @validator("name", always=True)
    def generate_db_name(cls, v) -> str:
        return safe_name(v)

    def get_uri(self) -> str:
        creds = f"{self.user}:{self.password}@" if self.user and self.password else ""
        return f"{self.protocol}://{creds}{self.host}:{str(self.port)}"


class DocConfig(ModelBase):
    """Documentation config model"""

    openapi_url: str = "/openapi.json"
    swaggerui_url: str = "/docs"
    redoc_url: str = "/redoc"


class InfoConfig(ModelBase):
    """General information config model"""

    platform_name: str = "Tekst"
    description: str = "An online text research platform"
    terms: HttpUrl = "https://www.example-tekst-instance.org/terms"
    contact_name: str = "Rick Sanchez"
    contact_url: HttpUrl = "https://www.example-tekst-instance.org/contact"
    contact_email: EmailStr = "rick.sanchez@example-tekst-instance.org"


class TekstInfoConfig(ModelBase):
    """
    Tekst platform information config model

    These values are not configurable. They are taken from the package infos and
    aren't meant to be changed by users creating an own instance of the platform.
    """

    name: str = Field("Tekst")
    version: str = Field(pkg_meta["version"])
    description: str = Field(pkg_meta["description"])
    website: HttpUrl = Field(pkg_meta["website"])
    license: str = Field(pkg_meta["license"])
    license_url: HttpUrl = Field(pkg_meta["license_url"])


class SecurityConfig(ModelBase):
    """Security config model"""

    secret: str = Field(default_factory=lambda: token_hex(32), min_length=16)
    closed_mode: bool = False
    users_active_by_default: bool = False
    enable_cookie_auth: bool = True
    enable_jwt_auth: bool = True
    auth_cookie_name: str = "tekstuserauth"
    auth_cookie_domain: str | None = None
    auth_cookie_lifetime: conint(ge=3600) = 43200
    access_token_lifetime: conint(ge=3600) = 43200
    auth_jwt_lifetime: int = conint(ge=3600)
    reset_pw_token_lifetime: conint(ge=600) = 3600
    verification_token_lifetime: conint(ge=600) = 3600
    csrf_cookie_name: str = "XSRF-TOKEN"
    csrf_header_name: str = "X-XSRF-TOKEN"


class EMailConfig(ModelBase):
    """Email-related things config model"""

    smtp_server: str | None = None
    smtp_port: int | None = 25
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_starttls: bool = True
    from_address: str = "noreply@example-tekst-instance.org"


class TekstConfig(BaseSettings):
    """Platform config model"""

    # basic
    dev_mode: bool = False
    web_path: str = "/"
    api_path: str = "/api"
    server_url: HttpUrl = "http://127.0.0.1:8000"
    user_files_dir: str = "userfiles"
    log_level: str = "warning"

    # uvicorn asgi binding
    dev_host: str = "127.0.0.1"
    dev_port: int = 8000

    # CORS
    cors_allow_origins: str | list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: str | list[str] = ["*"]
    cors_allow_headers: str | list[str] = ["*"]

    # special domain sub configs
    email: EMailConfig = EMailConfig()  # Email-related config
    security: SecurityConfig = SecurityConfig()  # security-related config
    db: DbConfig = DbConfig()  # db-related config (MongoDB)
    doc: DocConfig = DocConfig()  # documentation-related config (OpenAPI, Redoc)
    info: InfoConfig = InfoConfig()  # general platform information config
    tekst_info: TekstInfoConfig = TekstInfoConfig()  # Tekst information config

    @validator(
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        pre=True,
    )
    def split_cors(cls, v):
        if isinstance(v, list):
            return [str(e) for e in v]
        if isinstance(v, str):
            return [e.strip() for e in v.split(",")]
        raise TypeError("Value must be a string or list of strings")

    @validator("log_level")
    def uppercase_log_lvl(cls, v: str) -> str:
        return v.upper()

    class Config:
        env_file = _select_env_files()
        env_file_encoding = "utf-8"
        env_prefix = "TEKST_"
        env_nested_delimiter = "__"
        case_sensitive = False


@lru_cache
def get_config() -> TekstConfig:
    return TekstConfig()
