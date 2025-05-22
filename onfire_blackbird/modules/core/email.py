import asyncio
import time
from pathlib import Path

import aiohttp

from onfire_blackbird.modules.export.dump import dump_content
from onfire_blackbird.modules.utils.console import print_if_not_json
from onfire_blackbird.modules.utils.filter import apply_filters, filter_found_accounts
from onfire_blackbird.modules.utils.http_client import do_async_request
from onfire_blackbird.modules.utils.input import process_input
from onfire_blackbird.modules.utils.log import log_error
from onfire_blackbird.modules.utils.parse import extract_metadata
from onfire_blackbird.modules.utils.precheck import perform_pre_check
from onfire_blackbird.modules.whatsmyname.list_operations import read_list


# Verify account existence based on list args
async def check_site(site, method, url, session, semaphore, config, data=None, headers=None):
    return_data = {"name": site["name"], "url": url, "category": site["cat"], "status": "NONE", "metadata": None}
    async with semaphore:
        if site["pre_check"]:
            authenticated_headers = perform_pre_check(site["pre_check"], headers, config)
            headers = authenticated_headers
            if headers is False:
                return_data["status"] = "ERROR"
                return return_data

        response = await do_async_request(method, url, session, config, data, headers)
        if response is None:
            return_data["status"] = "ERROR"
            return return_data
        try:
            if response:
                if (site["e_string"] in response["content"]) and (site["e_code"] == response["status_code"]):
                    if (site["m_string"] not in response["content"]) and (site["m_code"] != response["status_code"]):
                        return_data["status"] = "FOUND"
                        print_if_not_json(
                            f"  ✔️  \[[cyan1]{site['name']}[/cyan1]] [bright_white]{response['url']}[/bright_white]"
                        )
                        if site["metadata"]:
                            extracted_metadata = extract_metadata(site["metadata"], response, site["name"], config)
                            if extracted_metadata is not None:
                                extracted_metadata.sort(key=lambda x: x["name"])
                                return_data["metadata"] = extracted_metadata
                        # Save response content to a .HTML file
                        if config.dump:
                            path = Path(config.save_directory) / f"dump_{config.current_email}"

                            result = dump_content(path, site, response, config)
                            if result is True and config.verbose:
                                print_if_not_json("      💾  Saved HTML data from found account")
                else:
                    return_data["status"] = "NOT-FOUND"
                    if config.verbose:
                        print_if_not_json(
                            f"  ❌ [[blue]{site['name']}[/blue]] [bright_white]{response['url']}[/bright_white]"
                        )
                return return_data
        except Exception as e:
            log_error(e, f"Coudn't check {site['name']} {url}", config)
            return return_data


# Control survey on list sites
async def fetch_results(email, config):
    original_email = email
    async with aiohttp.ClientSession() as session:
        tasks = []
        semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        for site in config.email_sites:
            if site["input_operation"] is not None:
                email = process_input(original_email, site["input_operation"], config)
            else:
                email = original_email
            url = site["uri_check"].replace("{account}", email)
            site_data = site["data"].replace("{account}", email) if site["data"] else None
            headers = site["headers"] if site["headers"] else None
            tasks.append(
                check_site(
                    site=site,
                    method=site["method"],
                    url=url,
                    session=session,
                    semaphore=semaphore,
                    config=config,
                    data=site_data,
                    headers=headers,
                )
            )
        tasks_results = await asyncio.gather(*tasks, return_exceptions=True)
        results = {"results": tasks_results, "email": email}
    return results


# Start email check and presents results to user
def verify_email(email, config):
    data = read_list("email", config)
    if data and isinstance(data, dict):
        sites_to_search = data["sites"]
    else:
        # Handle the case where data is False or not a dict
        sites_to_search = []

    config.email_sites = apply_filters(sites_to_search, config)

    print_if_not_json(f':play_button: Enumerating accounts with email "[cyan1]{email}[/cyan1]"')
    start_time = time.time()
    results = asyncio.run(fetch_results(email, config))
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
