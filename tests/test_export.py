import sys
import os
import json
from rich.console import Console

from blackbird import config
from blackbird.modules.export.csv import saveToCsv
from blackbird.modules.export.pdf import saveToPdf
from blackbird.modules.export.file_operations import createSaveDirectory
from datetime import datetime

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
    createSaveDirectory(config)
    with open(
        os.path.join(os.getcwd(), "tests", "data", "mock-email.json"),
        "r",
        encoding="UTF-8",
    ) as f:
        foundAccounts = json.load(f)
    result = saveToPdf(foundAccounts, "email", config)
    assert result


def test_export_csv():
    config.currentUser = "p1ngul1n0"
    config.pdf = False
    config.csv = True
    config.currentEmail = None
    createSaveDirectory(config)
    with open(
        os.path.join(os.getcwd(), "tests", "data", "mock-username.json"),
        "r",
        encoding="UTF-8",
    ) as f:
        foundAccounts = json.load(f)
    result = saveToCsv(foundAccounts, config)
    assert result
