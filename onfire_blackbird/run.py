import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

from onfire_blackbird import config
from onfire_blackbird.modules.core.email import fetch_results as fetch_email_results
from onfire_blackbird.modules.core.username import fetch_results as fetch_username_results
from onfire_blackbird.modules.ner.entity_extraction import inialize_nlp_model
from onfire_blackbird.modules.utils.console import print_if_not_json
from onfire_blackbird.modules.utils.filter import apply_filters, filter_found_accounts
from onfire_blackbird.modules.utils.user_agent import get_random_user_agent
from onfire_blackbird.modules.whatsmyname.list_operations import check_updates, read_list


async def verify_username_async(username: str, config, sites_to_search=None, metadata_params=None):
    """Async version of verify_username that doesn't use asyncio.run"""
    # Set default cache setting if not present
    if not hasattr(config, "use_cache"):
        config.use_cache = True

    if sites_to_search is None or metadata_params is None:
        data = read_list("username", config)
        if data and isinstance(data, dict):
            sites_to_search = data["sites"]
            config.metadata_params = read_list("metadata", config)
        else:
            # Handle the case where data is False or not a dict
            sites_to_search = []
            config.metadata_params = {}
    else:
        config.metadata_params = metadata_params

    # Apply filters once before running queries
    config.username_sites = apply_filters(sites_to_search, config)

    print_if_not_json(f':play_button: Enumerating accounts with username "[cyan1]{username}[/cyan1]"')
    start_time = time.time()
    results = await fetch_username_results(username, config)
    end_time = time.time()

    print_if_not_json(
        f":chequered_flag: Check completed in {round(end_time - start_time, 1)} seconds ({len(results['results'])} sites)"
    )

    if config.dump:
        print_if_not_json(
            f"💾  Dump content saved to '[cyan1]{config.current_user}_{config.date_raw}_blackbird/dump_{config.current_user}[/cyan1]'"
        )

    # Filter results to only found accounts
    found_accounts = list(filter(filter_found_accounts, results["results"]))
    config.username_found_accounts = found_accounts
    if len(found_accounts) <= 0:
        print_if_not_json("⭕ No accounts were found for the given username")

    return found_accounts


async def verify_email_async(email: str, config):
    """Async version of verify_email that doesn't use asyncio.run"""
    data = read_list("email", config)
    if data and isinstance(data, dict):
        sites_to_search = data["sites"]
    else:
        # Handle the case where data is False or not a dict
        sites_to_search = []

    config.email_sites = apply_filters(sites_to_search, config)

    print_if_not_json(f':play_button: Enumerating accounts with email "[cyan1]{email}[/cyan1]"')
    start_time = time.time()
    results = await fetch_email_results(email, config)
    end_time = time.time()

    print_if_not_json(
        f":chequered_flag: Check completed in {round(end_time - start_time, 1)} seconds ({len(results['results'])} sites)"
    )

    if config.dump:
        print_if_not_json(
            f"💾  Dump content saved to '[cyan1]{config.current_email}_{config.date_raw}_blackbird/dump_{config.current_email}[/cyan1]'"
        )

    # Filter results to only found accounts
    found_accounts = list(filter(filter_found_accounts, results["results"]))
    config.email_found_accounts = found_accounts

    if len(found_accounts) <= 0:
        print_if_not_json("⭕ No accounts were found for the given email")

    return found_accounts


async def run(
    usernames: Optional[list[str]] = None,
    emails: Optional[list[str]] = None,
    json_output: bool = False,
    no_nsfw: bool = False,
    verbose: bool = False,
    ai: bool = False,
    timeout: int = 30,
    max_concurrent_requests: int = 30,
    no_update: bool = False,
    dump: bool = False,
    proxy: Optional[str] = None,
    filter_param: Optional[str] = None,
    permute: bool = False,
    permuteall: bool = False,
    use_cache: bool = True,
    instagram_session_id: Optional[str] = None,
) -> dict:
    """
    Run Blackbird directly from Python code.

    Args:
        usernames: List of usernames to search for
        emails: List of emails to search for
        json_output: Whether to format output as JSON
        no_nsfw: Removes NSFW sites from the search
        verbose: Show verbose output
        ai: Extract metadata with AI
        timeout: Timeout in seconds for each HTTP request
        max_concurrent_requests: Maximum number of concurrent requests allowed
        no_update: Don't update sites lists
        dump: Dump HTML content for found accounts
        proxy: Proxy to send HTTP requests through
        filter_param: Filter sites to be searched by list property value (e.g. "cat=social")
        permute: Permute usernames, ignoring single elements
        permuteall: Permute usernames, all elements
        use_cache: Use cache for HTTP requests
        instagram_session_id: Instagram session ID for Instagram-specific data

    Returns:
        A dictionary containing the results
    """
    # Initialize config with core parameters first
    setattr(config, "verbose", verbose)

    # Initialize console
    console = Console()
    setattr(config, "console", console)

    # Set user agent (requires verbose and console to be initialized)
    user_agent = get_random_user_agent(config)
    setattr(config, "user_agent", user_agent)

    # Now set all other config parameters
    setattr(config, "username", usernames)
    setattr(config, "email", emails)
    setattr(config, "json", json_output)
    setattr(config, "no_nsfw", no_nsfw)
    setattr(config, "ai", ai)
    setattr(config, "timeout", timeout)
    setattr(config, "max_concurrent_requests", max_concurrent_requests)
    setattr(config, "no_update", no_update)
    setattr(config, "dump", dump)
    setattr(config, "proxy", proxy)
    setattr(config, "filter", filter_param)
    setattr(config, "permute", permute)
    setattr(config, "permuteall", permuteall)
    setattr(config, "use_cache", use_cache)
    setattr(config, "instagram_session_id", instagram_session_id)

    # Initialize base directory and paths
    setattr(config, "BASE_DIR", Path(__file__).parent.parent)

    # Initialize config dates
    date_raw = datetime.now().strftime("%m_%d_%Y")
    date_pretty = datetime.now().strftime("%B %d, %Y")
    setattr(config, "date_raw", date_raw)
    setattr(config, "date_pretty", date_pretty)

    # Initialize other required attributes
    setattr(config, "username_found_accounts", None)
    setattr(config, "email_found_accounts", None)
    setattr(config, "current_user", None)
    setattr(config, "current_email", None)

    # Update site lists if needed
    if not no_update:
        check_updates(config)

    # Initialize AI model if needed
    if ai:
        inialize_nlp_model(config)
        setattr(config, "ai_model", True)

    combined_results = {"username_results": [], "email_results": []}

    # Process usernames
    if usernames:
        for username in usernames:
            setattr(config, "current_user", username)
            found_accounts = await verify_username_async(username, config)
            if found_accounts:
                result = {
                    "date": date_pretty,
                    "target": username,
                    "total_found": len(found_accounts),
                    "accounts": [],
                }

                for account in found_accounts:
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

                combined_results["username_results"].append(result)

            # Reset for next username
            setattr(config, "current_user", None)
            setattr(config, "username_found_accounts", None)

    # Process emails
    if emails:
        for email in emails:
            setattr(config, "current_email", email)
            found_accounts = await verify_email_async(email, config)
            if found_accounts:
                result = {
                    "date": date_pretty,
                    "target": email,
                    "total_found": len(found_accounts),
                    "accounts": [],
                }

                for account in found_accounts:
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

                combined_results["email_results"].append(result)

            # Reset for next email
            setattr(config, "current_email", None)
            setattr(config, "email_found_accounts", None)

    return combined_results
