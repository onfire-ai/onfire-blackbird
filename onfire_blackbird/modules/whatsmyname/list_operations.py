import json
import os
from typing import Optional

from requests import Response

from onfire_blackbird.config import USERNAME_LIST_URL
from onfire_blackbird.modules.utils.console import print_if_not_json
from onfire_blackbird.modules.utils.hash import hash_json
from onfire_blackbird.modules.utils.http_client import do_sync_request
from onfire_blackbird.modules.utils.log import log_error


# Read list file and return content
def read_list(option: str, config) -> dict | bool:
    if option == "username":
        with open(config.username_list_path, "r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    elif option == "email":
        with open(config.email_list_path, "r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    elif option == "metadata":
        with open(config.username_metadata_list_path, "r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    else:
        return False


# Download .JSON file list from defined URL
def download_list(config):
    response: Optional[Response] = do_sync_request("GET", USERNAME_LIST_URL, config)
    if response and hasattr(response, "json"):
        with open(config.username_list_path, "w", encoding="UTF-8") as f:
            json.dump(response.json(), f, indent=4, ensure_ascii=False)


# Check for changes in remote list
def check_updates(config):
    if os.path.isfile(config.username_list_path):
        print_if_not_json(":counterclockwise_arrows_button: Checking for updates...")
        try:
            data = read_list("username", config)
            currentListHash = hash_json(data)
            response: Optional[Response] = do_sync_request("GET", USERNAME_LIST_URL, config)
            if response and hasattr(response, "json"):
                remoteListHash = hash_json(response.json())
                if currentListHash != remoteListHash:
                    print_if_not_json(":counterclockwise_arrows_button: Updating...")
                    download_list(config)
                else:
                    print_if_not_json("✔️  Sites List is up to date")
        except Exception as e:
            print_if_not_json(":police_car_light: Coudn't read local list")
            print_if_not_json(":down_arrow: Downloading site list")
            log_error(e, "Coudn't read local list", config)
            download_list(config)
    else:
        print_if_not_json(":globe_with_meridians: Downloading site list")
        download_list(config)
