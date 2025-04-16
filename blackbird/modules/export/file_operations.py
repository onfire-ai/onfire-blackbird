from pathlib import Path

from rich.markup import escape


# Creates directory to save PDF, CSV and HTML content
def create_save_directory(config):
    folderName = generate_name(config)

    strPath = Path(__file__).parent.parent.parent.parent / "results" / folderName
    config.saveDirectory = str(strPath)
    if not strPath.exists():
        strPath.mkdir(parents=True, exist_ok=True)
        if config.verbose:
            config.console.print(escape(f"🆕 Created directory to save search data [{folderName}]"))

    if config.dump:
        if config.currentUser:
            create_dump_directory(config.currentUser, config)

        if config.currentEmail:
            create_dump_directory(config.currentEmail, config)

    if config.pdf:
        if config.currentUser:
            create_images_directory(config.currentUser, config)

        if config.currentEmail:
            create_images_directory(config.currentEmail, config)

    return True


def create_dump_directory(identifier, config):
    folderName = f"dump_{identifier}"
    strPath = Path(config.saveDirectory) / folderName
    if not strPath.exists():
        if config.verbose:
            config.console.print(escape(f"🆕 Created directory to save dump data [{folderName}]"))
        strPath.mkdir(parents=True, exist_ok=True)


def create_images_directory(identifier, config):
    folderName = f"images_{identifier}"
    strPath = Path(config.saveDirectory) / folderName
    if not strPath.exists():
        if config.verbose:
            config.console.print(escape(f"🆕 Created directory to save images [{folderName}]"))
        strPath.mkdir(parents=True, exist_ok=True)


def generate_name(config, extension=None):
    if config.currentUser:
        folderName = f"{config.currentUser}_{config.dateRaw}_blackbird"
    elif config.currentEmail:
        folderName = f"{config.currentEmail}_{config.dateRaw}_blackbird"

    if extension:
        folderName = folderName + "." + extension

    return folderName
