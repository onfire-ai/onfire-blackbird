from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from rich.console import Console

# Base directory for relative paths
BASE_DIR = Path(__file__).parent.parent

# List directory
LIST_DIRECTORY = "data"

# Username List
USERNAME_LIST_URL = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
USERNAME_LIST_FILENAME = "wmn-data.json"
USERNAME_LIST_PATH = BASE_DIR / LIST_DIRECTORY / USERNAME_LIST_FILENAME
USERNAME_METADATA_LIST_FILENAME = "wmn-metadata.json"
USERNAME_METADATA_LIST_PATH = BASE_DIR / LIST_DIRECTORY / USERNAME_METADATA_LIST_FILENAME

# Email List
EMAIL_LIST_FILENAME = "email-data.json"
EMAIL_LIST_PATH = BASE_DIR / LIST_DIRECTORY / EMAIL_LIST_FILENAME

# Logs
LOG_DIRECTORY = "logs"
LOG_FILENAME = "blackbird.log"
LOG_PATH = BASE_DIR / LOG_DIRECTORY / LOG_FILENAME

# Assets
ASSETS_DIRECTORY = "assets"
FONTS_DIRECTORY = "fonts"
IMAGES_DIRECTORY = "img"


# PDF
FONT_REGULAR_FILE = "Montserrat-Regular.ttf"
FONT_BOLD_FILE = "Montserrat-Bold.ttf"
FONT_NAME_REGULAR = "Montserrat"
FONT_NAME_BOLD = "Montserrat-Bold"


class Config(BaseModel):
    # CLI Arguments
    username: Optional[list[str]] = None
    username_file: Optional[str] = None
    permute: bool = False
    permute_all: bool = False
    email: Optional[list[str]] = None
    email_file: Optional[str] = None
    csv: bool = False
    pdf: bool = False
    json: bool = False
    verbose: bool = False
    ai: bool = False
    filter: Optional[str] = None
    no_nsfw: bool = False
    dump: bool = False
    proxy: Optional[str] = None
    timeout: int = 30
    max_concurrent_requests: int = 30
    no_update: bool = False
    about: bool = False

    # Runtime values
    instagram_session_id: Optional[str] = None
    console: Optional[Console] = None
    date_raw: Optional[str] = None
    date_pretty: Optional[str] = None
    user_agent: Optional[str] = None
    username_found_accounts: Optional[list] = None
    email_found_accounts: Optional[list] = None
    current_user: Optional[str] = None
    current_email: Optional[str] = None
    ai_model: bool = False

    class Config:
        # Allow attribute assignment after instance creation
        arbitrary_types_allowed = True
        validate_assignment = False


# Create the default config instance
config = Config()
