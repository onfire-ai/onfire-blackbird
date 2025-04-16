import json
import os

from blackbird.modules.utils.hash import hash_json
from blackbird.modules.utils.http_client import do_sync_request
from blackbird.modules.utils.log import log_error


# Read list file and return content
def read_list(option, config):
    if option == "username":
        with open(config.USERNAME_LIST_PATH, "r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    elif option == "email":
        with open(config.EMAIL_LIST_PATH, "r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    elif option == "metadata":
        with open(config.USERNAME_METADATA_LIST_PATH, "r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    else:
        return False


# Download .JSON file list from defined URL
def download_list(config):
    response = do_sync_request("GET", config.USERNAME_LIST_URL, config)
    with open(config.USERNAME_LIST_PATH, "w", encoding="UTF-8") as f:
        json.dump(response.json(), f, indent=4, ensure_ascii=False)


# Check for changes in remote list
def check_updates(config):
    if os.path.isfile(config.USERNAME_LIST_PATH):
        config.console.print(":counterclockwise_arrows_button: Checking for updates...")
        try:
            data = read_list("username", config)
            currentListHash = hash_json(data)
            response = do_sync_request("GET", config.USERNAME_LIST_URL, config)
            remoteListHash = hash_json(response.json())
            if currentListHash != remoteListHash:
                config.console.print(":counterclockwise_arrows_button: Updating...")
                download_list(config)
            else:
                config.console.print("✔️  Sites List is up to date")
        except Exception as e:
            config.console.print(":police_car_light: Coudn't read local list")
            config.console.print(":down_arrow: Downloading site list")
            log_error(e, "Coudn't read local list", config)
            download_list(config)
    else:
        config.console.print(":globe_with_meridians: Downloading site list")
        download_list(config)
