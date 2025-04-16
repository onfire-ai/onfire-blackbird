import csv
import os

from blackbird.modules.export.file_operations import generate_name
from blackbird.modules.utils.log import log_error


# Save results to CSV file
def save_to_csv(results, config):
    try:
        fileName = generate_name(config, "csv")
        path = os.path.join(config.saveDirectory, fileName)
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "url"])
            for result in results:
                writer.writerow([result["name"], result["url"]])
        config.console.print(f"💾  Saved results to '[cyan1]{fileName}[/cyan1]'")
        return True
    except Exception as e:
        log_error(e, "Coudn't saved results to CSV file!", config)
        return False
