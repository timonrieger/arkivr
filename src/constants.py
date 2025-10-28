import json
import requests
import dotenv
import os

dotenv.load_dotenv()

with open("static/data/data.json", "r") as f:
    data = json.load(f)

MEDIUM_CHOICES = data["medium"]
CATEGORY_CHOICES = data["category"]
TAGS_CHOICES = data["tags"]

RESSOURCE_SCHEMA = {
    "required": ["name", "link", "description", "category", "medium"],
    "optional": ["tags", "private"],
}
