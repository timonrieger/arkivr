import requests
import dotenv
import os

dotenv.load_dotenv()

NPOINT = os.getenv("NPOINT")
npoint_data = requests.get(url=NPOINT).json()

MEDIUM_CHOICES = npoint_data["medium"]
CATEGORY_CHOICES = npoint_data["category"]
TAGS_CHOICES = npoint_data["tags"]