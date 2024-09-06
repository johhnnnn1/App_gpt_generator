import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.urandom(24)
    GPT4_API_KEY = os.getenv("GPT4_API_KEY")
    AZURE_OAI_ENDPOINT = os.getenv("AZURE_OAI_ENDPOINT")
    AZURE_OAI_KEY = os.getenv("AZURE_OAI_KEY")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")
    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")

config = Config()
