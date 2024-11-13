"""Configure application logging"""

import logging

# Create a logger
logger = logging.getLogger("AGRITECH-TZ")
logger.setLevel(logging.DEBUG)  # Set log level to DEBUG to capture all levels

# Create a console handler
console_handler = logging.StreamHandler()

# Create a formatter and set it for the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)
