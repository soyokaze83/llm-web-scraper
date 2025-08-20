import itertools
import json
import os

import pytest
from dotenv import load_dotenv

load_dotenv()


class KeyRotator:
    """
    A simple class to rotate through a list of API keys.
    The purpose is to simply avoid rate limit errors.
    """

    def __init__(self):
        self.keys = os.environ["TEST_API_KEYS"].split(",")
        if not all(self.keys):
            raise ValueError("TEST_API_KEYS not found in .env file or is empty.")
        self._cycle = itertools.cycle(self.keys)
        print(f"\n--- (KeyRotator Initialized with {len(self.keys)} keys) ---")

    def get_next_key(self):
        """Returns the next key in the cycle."""
        return next(self._cycle)


# Initializea key rotator as a global fixture
key_rotator = KeyRotator()


def load_test_cases():
    """Loads test cases from the generated JSON file."""
    try:
        with open("test_cases.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return [(data["url"], task) for task in data["tasks"]]
    except FileNotFoundError:
        pytest.skip("Could not find test_cases.json. Run generate_test_cases.py first.")
        return []
