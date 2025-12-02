"""
Configuration for DataHowLab SDK examples.

Environment Variables:
    DHL_BASE_URL: Base URL for the DataHowLab API (default: https://example.datahowlab.ch/)
    DHL_PROJECT: Project name to use in examples (default: SDK Test)
"""

import os

# Base URL for DataHowLab API - can be overridden via environment variable
DHL_BASE_URL = os.getenv("DHL_BASE_URL", "https://example.datahowlab.ch/")

# Default project name for examples - can be overridden via environment variable
DHL_PROJECT = os.getenv("DHL_PROJECT", "SDK Test")
