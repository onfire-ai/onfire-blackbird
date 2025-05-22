import re

from onfire_blackbird.modules.utils.console import print_if_not_json


def access_json_property(data, path_config):
    try:
        property_value = data
        for key in path_config:
            property_value = property_value[key]
        return property_value
    except Exception:
        return False


def access_html_regex(data, pattern):
    try:
        match = re.search(pattern, data)
        if match:
            return match.group(1).replace("\n", "")
    except Exception:
        return False


def download_image(link, site, config):
    if link:
        try:
            import requests

            response = requests.get(link, headers={}, stream=True, timeout=5)

            if response.status_code == 200:
                from pathlib import Path

                if config.currentUser:
                    path = Path(config.saveDirectory) / f"images_{config.currentUser}" / f"{site}_image.jpg"
                else:
                    path = Path(config.saveDirectory) / f"images_{config.currentEmail}" / f"{site}_image.jpg"

                with open(path, "wb") as file:
                    for chunk in response:
                        file.write(chunk)
                return True
        except Exception:
            return False
    return None


def extract_metadata(metadata, response, site, config):
    extractedMetadata = []
    for params in metadata:
        metadataReturn = params
        prefix = params["prefix"] if "prefix" in params else False

        if params["schema"] == "JSON":
            returnValue = access_json_property(response["json"], params["path"])
        elif params["schema"] == "HTML":
            returnValue = access_html_regex(response["content"], params["path"])
        else:
            return None

        if returnValue:
            if params["type"] == "String" and returnValue:
                if isinstance(returnValue, str):
                    returnValue = str(returnValue.replace("\n", ""))
                if prefix:
                    metadataReturn["value"] = prefix + returnValue
                else:
                    metadataReturn["value"] = returnValue
                print_if_not_json(f"      :right_arrow:  {metadataReturn['name']}: {metadataReturn['value']}")
            elif params["type"] == "Array" and returnValue:
                metadataReturn["value"] = []
                print_if_not_json(f"      :right_arrow:  {metadataReturn['name']}:")
                for value in returnValue:
                    itemValue = access_json_property(value, metadataReturn["item-path"])
                    metadataReturn["value"].append(itemValue)
                    print_if_not_json(f"         :blue_circle: {itemValue}")
            elif params["type"] == "Image" and returnValue:
                metadataReturn["downloaded"] = False
                if prefix:
                    metadataReturn["value"] = prefix + returnValue
                else:
                    metadataReturn["value"] = returnValue
                print_if_not_json(f"      :right_arrow:  {metadataReturn['name']}: {metadataReturn['value']}")
                if config.pdf:
                    metadataReturn = download_image(metadataReturn, site, config)
            extractedMetadata.append(metadataReturn)

    return extractedMetadata


def remove_duplicates(items):
    seen = set()
    unique_items = []
    for item in items:
        path_tuple = tuple(item["path"]) if item["path"] is not None else ()
        identifier = (item["schema"], item["type"], item["name"], path_tuple)
        if identifier not in seen:
            seen.add(identifier)
            unique_items.append(item)
    return unique_items
