from datetime import datetime

import pytest
from rich.console import Console

from onfire_blackbird import verify_email, verify_username
from onfire_blackbird.config import Config
from onfire_blackbird.modules.utils.user_agent import get_random_user_agent
from onfire_blackbird.modules.whatsmyname.list_operations import check_updates


@pytest.fixture
def setup_config():
    config = Config(
        no_nsfw=False,
        proxy=None,
        verbose=False,
        timeout=30,
        dump=True,
        csv=False,
        pdf=False,
        filter="name=Gravatar",
        console=Console(),
        max_concurrent_requests=30,
        date_raw=datetime.now().strftime("%m_%d_%Y"),
        date_pretty=datetime.now().strftime("%B %d, %Y"),
    )
    config.user_agent = get_random_user_agent(config)

    check_updates(config)
    return config


def test_verify_email(setup_config):
    result = verify_email("john@gmail.com", setup_config)
    assert result


def test_verify_username(setup_config):
    result = verify_username("p1ngul1n0", setup_config)
    assert result
