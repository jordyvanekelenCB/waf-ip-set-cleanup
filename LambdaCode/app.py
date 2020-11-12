""" Entry point file """

import os
import logging
import configparser
from http_flood_clean import HTTPFloodClean

# Setup logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Setup config parser
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))


# pylint: disable=W0613
def lambda_handler(event, context):
    """ Entry point of the Lambda function """

    # Activate HTTP flood clean
    http_clean_results = HTTPFloodClean(CONFIG).clean_http_flood()

    # Print the results
    print_results(http_clean_results)


def print_results(http_clean_results_obj):
    """ Prints results to screen """

    block_list_queue_expired = http_clean_results_obj['block_list_queue_expired']
    block_list_ip_set_expired = http_clean_results_obj['block_list_ip_set_expired']

    LOGGER.info('================================ Http flood clean results ================================')

    for ip_address in block_list_ip_set_expired:
        # pylint: disable=W1202
        LOGGER.info("Finding: Removed client ip: {0} from IP Set".format(ip_address))

    for ip_address in block_list_queue_expired:
        # pylint: disable=W1202
        LOGGER.info("Finding: Removed client ip: {0} from queue".format(ip_address))
