import re
import sys

from blackbird.modules.utils.console import print_if_not_json


def filter_found_accounts(site):
    if "status" in site and site["status"] == "FOUND":
        return True
    else:
        return False


def parse_filter(filter):
    pattern = r"(\w+)([=~><!]+)([^ ]+)\s*(and|or)?\s*"
    matches = re.findall(pattern, filter)

    conditions = []
    logical_ops = []

    for match in matches:
        conditions.append((match[0], match[1], match[2]))
        if match[3]:
            logical_ops.append(match[3])

    return conditions, logical_ops


def evaluate_condition(prop, operator, value, site):
    prop = prop.lower()
    value = value.lower()
    if prop not in site:
        return False

    site_value = str(site[prop])
    site_value = site_value.lower()

    if operator == "=":
        return site_value == value
    elif operator == "~":
        return value in site_value
    elif operator == ">":
        return float(site_value) > float(value)
    elif operator == "<":
        return float(site_value) < float(value)
    elif operator == ">=":
        return float(site_value) >= float(value)
    elif operator == "<=":
        return float(site_value) <= float(value)
    elif operator == "!=":
        return site_value != value
    else:
        return False


def filter_accounts(filter, site):
    conditions, logical_ops = parse_filter(filter)
    result = evaluate_condition(*conditions[0], site)

    if not conditions:
        print_if_not_json('⭕ Filter is not in correct format. Format should be --filter "property=value"')
        sys.exit()
    # Evaluate remaining conditions and combine using logical operators
    for i in range(1, len(conditions)):
        next_result = evaluate_condition(*conditions[i], site)

        if logical_ops[i - 1] == "and":
            result = result and next_result
        elif logical_ops[i - 1] == "or":
            result = result or next_result

    return result


def filter_nsfw(site):
    if site["cat"] == "xx NSFW xx":
        return False
    else:
        return True


def apply_filters(sitesToSearch, config):
    if config.filter:
        sitesToSearch = list(filter(lambda x: filter_accounts(config.filter, x), sitesToSearch))
        if (len(sitesToSearch)) <= 0:
            print_if_not_json(f"⭕ No sites found for the given filter {config.filter}")
            sys.exit()
        else:
            print_if_not_json(f':page_with_curl: Applied "{config.filter}" filter to sites [{len(sitesToSearch)}]')

    if config.no_nsfw:
        sitesToSearch = list(filter(lambda x: filter_nsfw(x), sitesToSearch))
        if (len(sitesToSearch)) <= 0:
            print_if_not_json("⭕ No remaining sites to be searched after NSFW filtering")
            sys.exit()
        else:
            print_if_not_json(f":page_with_curl: Filtered NSFW sites [{len(sitesToSearch)}]")

    return sitesToSearch
