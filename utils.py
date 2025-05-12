import os
import sys
import re


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')


def normalize_path(path, base_dir):
    abs_path = os.path.abspath(path)
    try:
        return os.path.relpath(abs_path, base_dir)
    except ValueError:
        return abs_path