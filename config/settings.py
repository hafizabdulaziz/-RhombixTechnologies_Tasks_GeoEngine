import os
from dotenv import load_dotenv

load_dotenv()

IP_API_URL = os.getenv("IP_API_URL", "http://ip-api.com/json/")
TIMEOUT = int(os.getenv("TIMEOUT", "5"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///geoengine.db")
