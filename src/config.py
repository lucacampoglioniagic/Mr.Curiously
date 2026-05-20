"""Carica variabili d'ambiente e le espone come oggetto Config tipizzato."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Instagram
    ig_user_id: str
    ig_access_token: str
    ig_username: str
    meta_app_id: str
    meta_app_secret: str

    # Cloudflare R2
    r2_account_id: str
    r2_access_key: str
    r2_secret_key: str
    r2_bucket: str
    r2_public_url: str
    r2_endpoint: str

    # AI providers
    openai_api_key: str
    anthropic_api_key: str

    # TikTok (opzionale)
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    tiktok_access_token: str = ""
    tiktok_open_id: str = ""


def load_config() -> Config:
    def require(key: str) -> str:
        val = os.environ.get(key, "")
        if not val:
            raise EnvironmentError(f"Variabile d'ambiente mancante: {key}")
        return val

    return Config(
        ig_user_id=require("IG_USER_ID"),
        ig_access_token=require("IG_ACCESS_TOKEN"),
        ig_username=os.environ.get("IG_USERNAME", ""),
        meta_app_id=os.environ.get("META_APP_ID", ""),
        meta_app_secret=os.environ.get("META_APP_SECRET", ""),
        r2_account_id=require("R2_ACCOUNT_ID"),
        r2_access_key=require("R2_ACCESS_KEY"),
        r2_secret_key=require("R2_SECRET_KEY"),
        r2_bucket=require("R2_BUCKET"),
        r2_public_url=require("R2_PUBLIC_URL"),
        r2_endpoint=require("R2_ENDPOINT"),
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        tiktok_client_key=os.environ.get("TIKTOK_CLIENT_KEY", ""),
        tiktok_client_secret=os.environ.get("TIKTOK_CLIENT_SECRET", ""),
        tiktok_access_token=os.environ.get("TIKTOK_ACCESS_TOKEN", ""),
        tiktok_open_id=os.environ.get("TIKTOK_OPEN_ID", ""),
    )
