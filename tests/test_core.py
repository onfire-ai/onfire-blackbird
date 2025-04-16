from datetime import datetime

from rich.console import Console

from blackbird import config, verify_email, verify_username
from blackbird.modules.utils.userAgent import get_random_user_agent
from blackbird.modules.whatsmyname.list_operations import check_updates

config.no_nsfw = None
config.proxy = None
config.verbose = None
config.timeout = None
config.dump = True
config.csv = None
config.pdf = None
config.filter = "name=Gravatar"
config.console = Console()
config.userAgent = get_random_user_agent(config)
config.max_concurrent_requests = 30

config.dateRaw = datetime.now().strftime("%m_%d_%Y")
config.datePretty = datetime.now().strftime("%B %d, %Y")

check_updates(config)


def test_verify_email():
    config.currentEmail = "john@gmail.com"
    result = verify_email(config.currentEmail, config)
    assert result


def test_verify_username():
    config.currentUser = "p1ngul1n0"
    result = verify_username(config.currentUser, config)
    assert result
