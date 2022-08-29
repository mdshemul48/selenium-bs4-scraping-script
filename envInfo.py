from dotenv import load_dotenv
from os import getenv

load_dotenv()

SITE_LINK = getenv("SITE_LINK")
SITE_EMAIL = getenv("SITE_EMAIL")
SITE_PASSWORD = getenv("SITE_PASSWORD")
