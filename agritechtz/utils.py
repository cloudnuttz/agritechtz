"""Utilities module"""

import re
import math


# Function to convert camelCase to snake_case
def camel_to_snake(name: str):
    """Convert camel case to snake case"""
    name = re.sub(r"\s+", "_", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def sanitize_data(data):
    """
    Recursively replace NaN values with None in dictionaries or lists.
    """
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    if isinstance(data, list):
        return [sanitize_data(item) for item in data]
    if math.isnan(float(data)):
        return None
    return data
