# app settings env constants
import os
from dotenv import load_dotenv

load_dotenv()

# Example of environment config
APP_NAME = os.getenv("APP_NAME", "Shadow ")
DEBUG = os.getenv("DEBUG", "True") == "True"