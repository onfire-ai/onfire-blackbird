import random
from pathlib import Path


def get_random_user_agent(config):
    path = Path(__file__).parent.parent.parent.parent / "data" / "useragents.txt"
    user_agents = open(path).read().splitlines()
    user_agent = random.choice(user_agents)
    if config.verbose:
        config.console.print(f':id: Selected random User-Agent "{user_agent}"')
    return user_agent
