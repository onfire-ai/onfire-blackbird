import os


def is_file(fileName):
    return os.path.isfile(fileName)


def get_lines_from_file(fileName):
    try:
        with open(fileName) as f:
            lines = f.read().splitlines()
            return lines
    except Exception:
        return False
