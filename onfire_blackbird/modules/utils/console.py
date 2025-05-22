from onfire_blackbird.config import config


def print_if_not_json(*args, **kwargs):
    """
    Print to console only if not in JSON mode.
    This is a wrapper around config.console.print that respects the JSON flag.

    All arguments are passed directly to config.console.print
    """
    if not hasattr(config, "json") or not config.json_output:
        if hasattr(config, "console") and config.console is not None:
            config.console.print(*args, **kwargs)
