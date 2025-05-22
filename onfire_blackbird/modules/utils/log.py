import logging


def log_error(e, message, config):
    if str(e) != "":
        error = str(e)
    else:
        error = repr(e)
    if "TimeoutError" in error:
        logging.debug(f"{message} | {error}")
    elif "Cannot connect to host" in error:
        logging.debug(f"{message} | {error}")
    else:
        logging.error(f"{message} | {error}")
    if config.verbose:
        config.console.print(f"⛔  {message}")
        config.console.print("     | An error occurred:")
        config.console.print(f"     | {error}")
