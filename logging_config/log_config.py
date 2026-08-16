import json
import logging.config
import os

def setup_logging():
    config_path = r"logging_config\config_log.json"
    with open(os.path(config_path)) as f:
        config = json.load(f)
    logging.config.dictConfig(config)