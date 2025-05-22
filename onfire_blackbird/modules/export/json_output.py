import json
import sys


def output_json(accounts, config):
    """
    Output account data as JSON to stdout.

    This function formats the found accounts data as JSON and prints it to stdout.
    It's designed to be used with the --json flag.

    Args:
        accounts: The list of found accounts
        config: The configuration object
    """

    result = {
        "date": config.datePretty,
        "target": config.currentUser if config.currentUser else config.currentEmail,
        "total_found": len(accounts),
        "accounts": [],
    }

    for account in accounts:
        account_data = {
            "name": account["name"],
            "url": account["url"],
            "category": account["category"],
            "status": account["status"],
        }

        # Add metadata if available
        if account["metadata"]:
            metadata = {}
            for data in account["metadata"]:
                metadata[data["name"]] = data["value"]
            account_data["metadata"] = metadata

        result["accounts"].append(account_data)

    # Output as JSON to stdout
    json.dump(result, sys.stdout)
    # Add a newline for shell friendliness
    sys.stdout.write("\n")
    sys.stdout.flush()
