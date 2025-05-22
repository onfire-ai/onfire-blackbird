import hashlib
import json


# Return MD5 HASH for given JSON
def hash_json(jsonData):
    jsonString = json.dumps(jsonData, sort_keys=True)
    return hashlib.md5(jsonString.encode("utf-8")).hexdigest()
