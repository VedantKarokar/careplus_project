import json
import logging.config

def setup_logging(name = __name__):
    config_path = r"config\logging.json"
    with open(config_path) as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    logger = logging.getLogger(name)
    return logger
