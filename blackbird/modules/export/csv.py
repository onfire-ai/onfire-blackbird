import csv
from pathlib import Path

from blackbird.modules.export.file_operations import generate_name
from blackbird.modules.utils.console import print_if_not_json
from blackbird.modules.utils.log import log_error


# Save results to CSV file
def save_to_csv(foundAccounts, config):
    try:
        fileName = generate_name(config, "csv")
        path = Path(config.saveDirectory) / fileName

        with open(path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Report generated on", config.datePretty])
            if config.currentUser:
                writer.writerow(["Target", config.currentUser])
            else:
                writer.writerow(["Target", config.currentEmail])
            writer.writerow(["Site", "Text", "Url"])

            for account in foundAccounts:
                siteState = "✓" if account["status"] == "FOUND" else "✕"
                writer.writerow([account["name"], siteState, account["url"]])

        print_if_not_json(f"💾  Saved results to '[cyan1]{fileName}[/cyan1]'")
        return True
    except Exception as e:
        log_error(e, "Coudn't save results to CSV file!", config)
        return False
