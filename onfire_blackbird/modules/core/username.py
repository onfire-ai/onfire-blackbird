import asyncio
import os
import sys
import time
from pathlib import Path

import aiohttp

from onfire_blackbird.modules.export.dump import dump_content
from onfire_blackbird.modules.ner.entity_extraction import extract_data_with_ai
from onfire_blackbird.modules.sites.instagram import get_instagram_account_info
from onfire_blackbird.modules.utils.console import print_if_not_json
from onfire_blackbird.modules.utils.filter import apply_filters, filter_found_accounts
from onfire_blackbird.modules.utils.http_client import do_async_request
from onfire_blackbird.modules.utils.log import log_error
from onfire_blackbird.modules.utils.parse import extract_metadata, remove_duplicates
from onfire_blackbird.modules.whatsmyname.list_operations import read_list

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Simple cache for storing username results
_username_cache = {}


# Verify account existence based on list args
async def check_site(site, method, url, session, semaphore, config):
    return_data = {"name": site["name"], "url": url, "category": site["cat"], "status": "NONE", "metadata": None}
    extracted_metadata = []

    async with semaphore:
        # Check cache first if enabled
        if hasattr(config, "use_cache") and config.use_cache:
            cache_key = f"{url}_{config.user_agent}_{config.proxy}"
            if cache_key in _username_cache:
                return _username_cache[cache_key]

        try:
            response = await do_async_request(method, url, session, config)
            if response is None:
                return_data["status"] = "ERROR"
                return return_data

            if response:
                if (site["e_string"] in response["content"]) and (site["e_code"] == response["status_code"]):
                    if (site["m_string"] not in response["content"]) and (
                        (site["m_code"] != response["status_code"]) if site["m_code"] != site["e_code"] else True
                    ):
                        return_data["status"] = "FOUND"
                        print_if_not_json(
                            f"  ✔️  \[[cyan1]{site['name']}[/cyan1]] [bright_white]{response['url']}[/bright_white]"
                        )

                        # Extract metadata sequentially
                        if site["name"] in config.metadata_params["sites"]:
                            metadata = extract_metadata(
                                config.metadata_params["sites"][site["name"]], response, site["name"], config
                            )
                            if metadata:
                                extracted_metadata.extend(metadata)

                        if config.ai and config.ai_model:
                            metadata = extract_data_with_ai(config, site, response["content"], response["json"])
                            if metadata:
                                extracted_metadata.extend(metadata)

                        if site["name"] == "Instagram":
                            if config.instagram_session_id:
                                metadata = get_instagram_account_info(
                                    config.current_user, config.instagram_session_id, config
                                )
                                if metadata and extracted_metadata:
                                    extracted_metadata.sort(key=lambda x: x["name"])
                                    extracted_metadata.extend(metadata)

                        if extracted_metadata and len(extracted_metadata) > 0:
                            extracted_metadata = remove_duplicates(extracted_metadata)
                            extracted_metadata.sort(key=lambda x: x["name"])
                            return_data["metadata"] = extracted_metadata

                        # Save response content to a .HTML file
                        if config.dump:
                            path = Path(config.save_directory) / f"dump_{config.current_user}"
                            result = dump_content(path, site, response, config)
                            if result is True and config.verbose:
                                print_if_not_json("      💾  Saved HTML data from found account")
                else:
                    return_data["status"] = "NOT-FOUND"
                    if config.verbose:
                        print_if_not_json(
                            f"  ❌ [[blue]{site['name']}[/blue]] [bright_white]{response['url']}[/bright_white]"
                        )

                # Store in cache
                if hasattr(config, "use_cache") and config.use_cache:
                    cache_key = f"{url}_{config.user_agent}_{config.proxy}"
                    _username_cache[cache_key] = return_data

                return return_data
        except asyncio.TimeoutError:
            log_error("Timeout", f"Request timed out for {site['name']} {url}", config)
            return_data["status"] = "ERROR"
            return return_data
        except Exception as e:
            log_error(e, f"Coudn't check {site['name']} {url}", config)
            return return_data


# Control survey on list sites
async def fetch_results(username, config):
    async with aiohttp.ClientSession() as session:
        tasks = []
        semaphore = asyncio.Semaphore(config.max_concurrent_requests)

        # Process sites in batches if there are many of them
        sites = config.username_sites
        batch_size = min(100, len(sites))  # Adjust batch size based on testing

        for i in range(0, len(sites), batch_size):
            batch = sites[i : i + batch_size]
            batch_tasks = []

            for site in batch:
                batch_tasks.append(
                    check_site(
                        site=site,
                        method="GET",
                        url=site["uri_check"].replace("{account}", username),
                        session=session,
                        semaphore=semaphore,
                        config=config,
                    )
                )

            # Process each batch with a small delay to avoid overwhelming the network
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            tasks.extend(batch_results)

            # Small delay between batches if needed
            if i + batch_size < len(sites) and len(sites) > 200:
                await asyncio.sleep(0.5)

        results = {"results": tasks, "username": username}
    return results


# Start username check and presents results to user
def verify_username(username, config, sites_to_search=None, metadata_params=None):
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
    results = asyncio.run(fetch_results(username, config))
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
