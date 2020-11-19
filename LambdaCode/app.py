""" Entry point file """

import os
import configparser
from http_flood_clean import HTTPFloodClean
from utilities import Diagnostics

# Setup config parser
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))


# pylint: disable=W0613
def lambda_handler(event, context) -> None:
    """ Entry point of the Lambda function """

    # Activate HTTP flood clean
    http_clean_results = HTTPFloodClean(CONFIG).clean_http_flood()

    # Print the results
    Diagnostics.print_results(http_clean_results)
