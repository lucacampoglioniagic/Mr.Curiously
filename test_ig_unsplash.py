import os, requests
from dotenv import load_dotenv
load_dotenv("c:/Users/Andal/source/repos/Social/.env")
TOKEN = os.environ['IG_ACCESS_TOKEN']
IG_USER_ID = os.environ['IG_USER_ID']
IMG = 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1080&h=1080&fit=crop&fm=jpg'
r = requests.post(
  f'https://graph.instagram.com/v21.0/{IG_USER_ID}/media',
  data={'image_url': IMG, 'caption': 'test unsplash', 'access_token': TOKEN}, timeout=30)
print('HTTP', r.status_code, r.text[:500])
