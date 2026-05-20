"""Genera JPEG, upload R2, pubblica su IG."""
import os, io, sys, time, requests
from dotenv import load_dotenv
import boto3
from botocore.client import Config
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY"],
    aws_secret_access_key=os.environ["R2_SECRET_KEY"],
    config=Config(signature_version="s3v4"),
    region_name="auto",
)

img = Image.new("RGB", (1080, 1080), (20, 30, 50))
d = ImageDraw.Draw(img)
try:
    font_big = ImageFont.truetype("arialbd.ttf", 90)
    font_sm = ImageFont.truetype("arial.ttf", 40)
except Exception:
    font_big = ImageFont.load_default()
    font_sm = font_big
d.text((110, 430), "Mr. Curiously", fill=(220, 230, 255), font=font_big)
d.text((110, 560), "First test post", fill=(150, 180, 220), font=font_sm)

buf = io.BytesIO()
img.save(buf, format="JPEG", quality=92, optimize=True)
buf.seek(0)
print(f"JPEG: {len(buf.getvalue())} bytes")

key = "test/first-post.jpg"
s3.put_object(
    Bucket=os.environ["R2_BUCKET"],
    Key=key,
    Body=buf.getvalue(),
    ContentType="image/jpeg",
)
PUBLIC = os.environ["R2_PUBLIC_URL"].rstrip("/")
IMAGE_URL = f"{PUBLIC}/{key}"
print(f"Uploaded: {IMAGE_URL}")

r = requests.get(IMAGE_URL, timeout=15)
print(f"Public check: HTTP {r.status_code}, ct={r.headers.get('content-type')}")

GRAPH = "https://graph.instagram.com/v21.0"
TOKEN = os.environ["IG_ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]
CAPTION = "Hello world 🧠\n\nFirst automated post.\n\n#curiousmind #facts"

print("\n[1/2] Creazione container...")
r1 = requests.post(
    f"{GRAPH}/{IG_USER_ID}/media",
    data={"image_url": IMAGE_URL, "caption": CAPTION, "access_token": TOKEN},
    timeout=30,
)
print(f"      HTTP {r1.status_code}: {r1.text[:300]}")
if r1.status_code != 200:
    sys.exit(1)
cid = r1.json()["id"]

for i in range(10):
    time.sleep(3)
    s = requests.get(
        f"{GRAPH}/{cid}",
        params={"fields": "status_code", "access_token": TOKEN},
        timeout=15,
    ).json()
    print(f"      status[{i}]: {s}")
    if s.get("status_code") == "FINISHED":
        break
    if s.get("status_code") == "ERROR":
        print("ERRORE elaborazione")
        sys.exit(1)

print("\n[2/2] Pubblicazione...")
r2 = requests.post(
    f"{GRAPH}/{IG_USER_ID}/media_publish",
    data={"creation_id": cid, "access_token": TOKEN},
    timeout=30,
)
print(f"      HTTP {r2.status_code}: {r2.text[:300]}")
if r2.status_code == 200:
    print(f"\n[OK] Pubblicato! Vai su https://www.instagram.com/{os.environ.get('IG_USERNAME','')}")
