"""Upload di file su Cloudflare R2."""
from __future__ import annotations

import io
from dataclasses import dataclass

import boto3
from botocore.client import Config as BotoConfig

from src.config import Config


@dataclass
class UploadResult:
    key: str
    public_url: str


def get_client(cfg: Config):
    return boto3.client(
        "s3",
        endpoint_url=cfg.r2_endpoint,
        aws_access_key_id=cfg.r2_access_key,
        aws_secret_access_key=cfg.r2_secret_key,
        config=BotoConfig(signature_version="s3v4"),
        region_name="auto",
    )


def upload_image(cfg: Config, image_bytes: bytes, key: str, content_type: str = "image/jpeg") -> UploadResult:
    """Carica bytes di un'immagine su R2 e restituisce l'URL pubblico."""
    client = get_client(cfg)
    client.put_object(
        Bucket=cfg.r2_bucket,
        Key=key,
        Body=image_bytes,
        ContentType=content_type,
    )
    public_url = f"{cfg.r2_public_url.rstrip('/')}/{key}"
    return UploadResult(key=key, public_url=public_url)
