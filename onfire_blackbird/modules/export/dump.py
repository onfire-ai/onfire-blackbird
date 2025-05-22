import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ""))

from onfire_blackbird.modules.utils.log import log_error


# Dump HTML data to a .html file
def dump_content(path, site, response, config):
    siteName = site["name"].replace(" ", "_")
    content = response["content"]
    extension = "txt"

    if response["headers"]["Content-Type"]:
        if "application/json" in response["headers"]["Content-Type"]:
            extension = "json"
            content = response["json"]
        elif "text/html" in response["headers"]["Content-Type"]:
            extension = "html"
            content = response["content"]

    fileName = f"{siteName}.{extension}"
    file_path = Path(path) / fileName

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            if response["json"]:
                json.dump(content, file)
            else:
                file.write(content)
        return True
    except Exception as e:
        log_error(e, "Coudn't DUMP data to HTML file!", config)
        return False
