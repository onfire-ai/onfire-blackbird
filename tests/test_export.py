import json
from datetime import datetime
from pathlib import Path

from rich.console import Console

from blackbird import config
from blackbird.modules.export.csv import save_to_csv
from blackbird.modules.export.file_operations import create_save_directory
from blackbird.modules.export.pdf import save_to_pdf

config.console = Console()

config.no_nsfw = None
config.proxy = None
config.verbose = None
config.timeout = None
config.dump = None
config.currentUser = None
config.currentEmail = None
config.dateRaw = datetime.now().strftime("%m_%d_%Y")
config.datePretty = datetime.now().strftime("%B %d, %Y")


def test_export_pdf():
    config.currentEmail = "john@gmail.com"
    config.pdf = True
    config.csv = False
    config.currentUser = None
    create_save_directory(config)
    with open(Path(__file__).parent / "data" / "mock-email.json", "r", encoding="UTF-8") as f:
        foundAccounts = json.load(f)
    result = save_to_pdf(foundAccounts, "email", config)
    assert result


def test_export_csv():
    config.currentUser = "p1ngul1n0"
    config.pdf = False
    config.csv = True
    config.currentEmail = None
    create_save_directory(config)
    with open(Path(__file__).parent / "data" / "mock-username.json", "r", encoding="UTF-8") as f:
        foundAccounts = json.load(f)
    result = save_to_csv(foundAccounts, config)
    assert result
