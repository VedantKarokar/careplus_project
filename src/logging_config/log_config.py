import json
import logging.config

def setup_logging(name: str):
    config_path = r"config\logging.json"
    with open(config_path) as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    custom_logger = logging.getLogger(name)
    return custom_logger
