import os
import csv

from blackbird.modules.export.file_operations import generateName
from blackbird.modules.utils.log import logError


# Save results to CSV file
def saveToCsv(results, config):
    try:
        fileName = generateName(config, "csv")
        path = os.path.join(config.saveDirectory, fileName)
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "url"])
            for result in results:
                writer.writerow([result["name"], result["url"]])
        config.console.print(f"💾  Saved results to '[cyan1]{fileName}[/cyan1]'")
        return True
    except Exception as e:
        logError(e, "Coudn't saved results to CSV file!", config)
        return False
