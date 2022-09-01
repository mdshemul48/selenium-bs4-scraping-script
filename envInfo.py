from dotenv import load_dotenv
from os import getenv

load_dotenv()

SITE_LINK = getenv("SITE_LINK")
SITE_EMAIL = getenv("SITE_EMAIL")
SITE_PASSWORD = getenv("SITE_PASSWORD")


DB_HOST = getenv("DB_HOST")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_DATABASE = getenv("DB_DATABASE")
