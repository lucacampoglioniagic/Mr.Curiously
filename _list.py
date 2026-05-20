import os
from dotenv import load_dotenv
import boto3
from botocore.client import Config
load_dotenv("c:/Users/Andal/source/repos/Social/.env")
s3 = boto3.client("s3",
    endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY"],
    aws_secret_access_key=os.environ["R2_SECRET_KEY"],
    config=Config(signature_version="s3v4"), region_name="auto")
r = s3.list_objects_v2(Bucket=os.environ["R2_BUCKET"])
for o in r.get("Contents", []):
    print(o["Key"], o["Size"])
