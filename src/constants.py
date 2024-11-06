import requests
import dotenv
import os

NPOINT = os.getenv("NPOINT")
npoint_data = requests.get(url=NPOINT).json()

MEDIUM_CHOICES = npoint_data["medium"]
CATEGORY_CHOICES = npoint_data["category"]
TOPIC_CHOICES = npoint_data["topic"]
TAGS_CHOICES = npoint_data["tags"]
ADMINS = npoint_data["admins"]