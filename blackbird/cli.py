import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from blackbird import config
from blackbird.modules.core.email import verify_email
from blackbird.modules.core.username import verify_username
from blackbird.modules.export.csv import save_to_csv
from blackbird.modules.export.file_operations import create_save_directory
from blackbird.modules.export.pdf import save_to_pdf
from blackbird.modules.ner.entity_extraction import inialize_nlp_model
from blackbird.modules.utils.console import print_if_not_json
from blackbird.modules.utils.file_operations import get_lines_from_file, is_file
from blackbird.modules.utils.permute import Permute
from blackbird.modules.utils.userAgent import get_random_user_agent
from blackbird.modules.whatsmyname.list_operations import check_updates

load_dotenv()


def initialize():
    log_dir = Path(config.BASE_DIR) / config.LOG_DIRECTORY
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=config.LOG_PATH, level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(
        prog="blackbird", description="An OSINT tool to search for accounts by username in social networks."
    )
    parser.add_argument("-u", "--username", nargs="*", type=str, help="One or more usernames to search.")
    parser.add_argument("-uf", "--username-file", help="The list of usernames to be searched.")
    parser.add_argument("--permute", action="store_true", help="Permute usernames, ignoring single elements.")
    parser.add_argument("--permuteall", action="store_true", help="Permute usernames, all elements.")
    parser.add_argument("-e", "--email", nargs="*", type=str, help="One or more email to search.")
    parser.add_argument("-ef", "--email-file", help="The list of emails to be searched.")
    parser.add_argument(
        "--csv", default=False, action=argparse.BooleanOptionalAction, help="Generate a CSV with the results."
    )
    parser.add_argument(
        "--pdf", default=False, action=argparse.BooleanOptionalAction, help="Generate a PDF with the results."
    )
    parser.add_argument(
        "--json", default=False, action=argparse.BooleanOptionalAction, help="Output results as JSON to stdout."
    )
    parser.add_argument(
        "-v", "--verbose", default=False, action=argparse.BooleanOptionalAction, help="Show verbose output."
    )
    parser.add_argument(
        "-ai", "--ai", default=False, action=argparse.BooleanOptionalAction, help="Extract Metadata with AI."
    )
    parser.add_argument("--filter", help='Filter sites to be searched by list property value.E.g --filter "cat=social"')
    parser.add_argument("--no-nsfw", action="store_true", help="Removes NSFW sites from the search.")
    parser.add_argument("--dump", action="store_true", help="Dump HTML content for found accounts.")
    parser.add_argument("--proxy", help="Proxy to send HTTP requests though.")
    parser.add_argument(
        "--timeout", type=int, default=30, help="Timeout in seconds for each HTTP request (Default is 30)."
    )
    parser.add_argument(
        "--max-concurrent-requests",
        type=int,
        default=30,
        help="Specify the maximum number of concurrent requests allowed. Default is 30.",
    )
    parser.add_argument("--no-update", action="store_true", help="Don't update sites lists.")
    parser.add_argument("--about", action="store_true", help="Show about information and exit.")
    args = parser.parse_args()

    # Store the necessary arguments to config Object
    config.username = args.username
    config.username_file = args.username_file
    config.permute = args.permute
    config.permuteall = args.permuteall
    config.csv = args.csv
    config.pdf = args.pdf
    config.json = args.json
    config.filter = args.filter
    config.no_nsfw = args.no_nsfw
    config.dump = args.dump
    config.proxy = args.proxy
    config.verbose = args.verbose
    config.ai = args.ai
    config.timeout = args.timeout
    config.max_concurrent_requests = args.max_concurrent_requests
    config.email = args.email
    config.email_file = args.email_file
    config.no_update = args.no_update
    config.about = args.about
    config.instagram_session_id = os.getenv("INSTAGRAM_SESSION_ID")

    config.console = Console()

    config.dateRaw = datetime.now().strftime("%m_%d_%Y")
    config.datePretty = datetime.now().strftime("%B %d, %Y")

    config.userAgent = get_random_user_agent(config)

    config.usernameFoundAccounts = None
    config.emailFoundAccounts = None

    config.currentUser = None
    config.currentEmail = None


def main():
    initialize()

    # ASCII art and other UI elements will only print if not in JSON mode
    print_if_not_json(
        """[red]
    ▄▄▄▄    ██▓    ▄▄▄       ▄████▄   ██ ▄█▀ ▄▄▄▄    ██▓ ██▀███  ▓█████▄
    ▓█████▄ ▓██▒   ▒████▄    ▒██▀ ▀█   ██▄█▒ ▓█████▄ ▓██▒▓██ ▒ ██▒▒██▀ ██▌
    ▒██▒ ▄██▒██░   ▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ ▒██▒ ▄██▒██▒▓██ ░▄█ ▒░██   █▌
    ▒██░█▀  ▒██░   ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄ ▒██░█▀  ░██░▒██▀▀█▄  ░▓█▄   ▌
    ░▓█  ▀█▓░██████▒▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄░▓█  ▀█▓░██░░██▓ ▒██▒░▒████▓
    ░▒▓███▀▒░ ▒░▓  ░▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒░▒▓███▀▒░▓  ░ ▒▓ ░▒▓░ ▒▒▓  ▒
    ▒░▒   ░ ░ ░ ▒  ░ ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░▒░▒   ░  ▒ ░  ░▒ ░ ▒░ ░ ▒  ▒
    ░    ░   ░ ░    ░   ▒   ░        ░ ░░ ░  ░    ░  ▒ ░  ░░   ░  ░ ░  ░
    ░          ░  ░     ░  ░░ ░      ░  ░    ░       ░     ░        ░
        ░                  ░                     ░               ░

    [/red]"""
    )
    print_if_not_json("           [white]Made with :beating_heart: by [red]Lucas 'P1ngul1n0' Antoniaci[/red] [/white]")

    if config.about:
        print_if_not_json(
            """
        Author: Lucas Antoniaci (p1ngul1n0)
        Description: Blackbird is an OSINT tool that perform reverse search in username and emails.
        About WhatsMyName Project: This tool search for accounts using data from the WhatsMyName project, which is an open-source tool developed by WebBreacher. WhatsMyName License: The WhatsMyName project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). More details (https://github.com/WebBreacher/WhatsMyName)
        """
        )
        sys.exit()

    if not config.username and not config.email and not config.username_file and not config.email_file:
        print_if_not_json("Either --username or --email is required")
        sys.exit()
    if not config.username and (config.permute or config.permuteall):
        print_if_not_json("Permutations requires --username")
        sys.exit()

    if config.no_update:
        print_if_not_json(":next_track_button:  Skipping update...")
    else:
        check_updates(config)

    if config.ai:
        inialize_nlp_model(config)
        config.aiModel = True

    if config.username_file:
        if is_file(config.username_file):
            config.username = get_lines_from_file(config.username_file)
            print_if_not_json(
                f':glasses: Successfully loaded {len(config.username)} usernames from "{config.username_file}"'
            )
        else:
            print_if_not_json(f'❌ Could not read file "{config.username_file}"')
            sys.exit()

    if config.username:
        if (config.permute or config.permuteall) and len(config.username) > 1:
            elements = " ".join(config.username)
            way = "all" if config.permuteall else "strict"
            permute = Permute(config.username)
            config.username = permute.gather(way)
            print_if_not_json(
                f":glasses: Successfully loaded {len(config.username)} usernames from permuting {elements}"
            )
        for user in config.username:
            config.currentUser = user
            if config.dump or config.csv or config.pdf:
                create_save_directory(config)
            found_accounts = verify_username(config.currentUser, config)
            if config.csv and found_accounts:
                save_to_csv(found_accounts, config)
            if config.pdf and found_accounts:
                save_to_pdf(found_accounts, "username", config)
            if config.json and found_accounts:
                from blackbird.modules.export.json_output import output_json

                output_json(found_accounts, config)
                # Exit after JSON output
                return
            config.currentUser = None
            config.usernameFoundAccounts = None

    if config.email_file:
        if is_file(config.email_file):
            config.email = get_lines_from_file(config.email_file)
            print_if_not_json(f':glasses: Successfully loaded {len(config.email)} emails from "{config.email_file}"')
        else:
            print_if_not_json(f'❌ Could not read file "{config.email_file}"')
            sys.exit()

    if config.email:
        for email in config.email:
            config.currentEmail = email
            if config.dump or config.csv or config.pdf:
                create_save_directory(config)
            email_found_accounts = verify_email(email, config)
            if config.csv and email_found_accounts:
                save_to_csv(email_found_accounts, config)
            if config.pdf and email_found_accounts:
                save_to_pdf(email_found_accounts, "email", config)
            if config.json and email_found_accounts:
                from blackbird.modules.export.json_output import output_json

                output_json(email_found_accounts, config)
                # Exit after JSON output
                return
            config.currentEmail = None
            config.emailFoundAccounts = None
