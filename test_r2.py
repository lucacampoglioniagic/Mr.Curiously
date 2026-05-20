"""Quick test: genera un'immagine PNG, la carica su R2, verifica che sia pubblica."""
import os, io, sys, requests
from dotenv import load_dotenv
import boto3
from botocore.client import Config
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
SECRET_KEY = os.environ["R2_SECRET_KEY"]
BUCKET     = os.environ["R2_BUCKET"]
PUBLIC_URL = os.environ["R2_PUBLIC_URL"].rstrip("/")
ENDPOINT   = os.environ["R2_ENDPOINT"]

img = Image.new("RGB", (1080, 1080), (20, 30, 50))
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("arial.ttf", 80)
except Exception:
    font = ImageFont.load_default()
d.text((180, 480), "Mr. Curiously\nR2 test OK", fill=(220, 230, 255), font=font, spacing=20)
buf = io.BytesIO()
img.save(buf, format="PNG", optimize=True)
buf.seek(0)
print(f"PNG generato: {len(buf.getvalue())} bytes")

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="auto",
)

key = "test/r2-smoke-test.png"
s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue(), ContentType="image/png")
print(f"Upload OK: s3://{BUCKET}/{key}")

public = f"{PUBLIC_URL}/{key}"
print(f"URL pubblico: {public}")

r = requests.get(public, timeout=15)
print(f"HTTP {r.status_code}, content-type={r.headers.get('content-type')}, bytes={len(r.content)}")
if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
    print("\n[OK] Test R2 completato con successo!")
    sys.exit(0)
else:
    print("\n[FAIL] L'URL pubblico non restituisce l'immagine.")
    print(r.text[:300])
    sys.exit(1)
