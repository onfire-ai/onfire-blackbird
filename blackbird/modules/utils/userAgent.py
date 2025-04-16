import random
from pathlib import Path


def get_random_user_agent(config):
    path = Path(__file__).parent.parent.parent.parent / "data" / "useragents.txt"
    userAgents = open(path).read().splitlines()
    userAgent = random.choice(userAgents)
    if config.verbose:
        config.console.print(f':id: Selected random User-Agent "{userAgent}"')
    return userAgent
