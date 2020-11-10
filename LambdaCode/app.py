import logging
import configparser
import os
from http_flood_clean import HTTPFloodClean

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Setup config parser
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))

def lambda_handler(event, context):

    # Activate HTTP flood clean
    http_clean_results = HTTPFloodClean(config).clean_http_flood()

    print_results(config, http_clean_results)


def print_results(http_clean_results_obj):

    block_list_queue_expired = http_clean_results_obj['block_list_queue_expired']
    block_list_ip_set_expired = http_clean_results_obj['block_list_ip_set_expired']

    logger.info('================================ Http flood clean results ================================')

    for ip in block_list_ip_set_expired:
        logger.info("Finding: Removed client ip: " + ip + " from IP Set")

    for ip in block_list_queue_expired:
        logger.info("Finding: Removed client ip: " + ip + " from queue")
