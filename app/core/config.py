import logging
from typing import Optional

from pydantic import BaseSettings, EmailStr

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_title: str = 'Приложение QRKot'
    app_description: str = (
        'Приложение для Благотворительного фонда поддержки котиков'
    )
    database_url: str = 'sqlite+aiosqlite:///./qrkot_sh.db'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    # Переменные для Google API
    type: Optional[str] = None
    project_id: Optional[str] = None
    private_key_id: Optional[str] = None
    private_key: Optional[str] = None
    client_email: Optional[str] = None
    client_id: Optional[str] = None
    auth_uri: Optional[str] = None
    token_uri: Optional[str] = None
    auth_provider_x509_cert_url: Optional[str] = None
    client_x509_cert_url: Optional[str] = None
    email: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            with open('private_key.pem', 'r') as key_file:
                self.private_key = key_file.read()
        except (FileNotFoundError, IOError):
            pass

    class Config:
        env_file = '.env'


settings = Settings()
