""" This module holds the Diagnostics class """

import logging

# Setup logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


class Diagnostics:
    """ This class is responsible for printing diagnostic results """

    def __str__(self):
        return self.__class__.__name__

    @staticmethod
    def print_results(http_clean_results_obj) -> None:
        """ Prints HTTP Flood clean results to screen """

        block_list_queue_expired = http_clean_results_obj['block_list_queue_expired']
        block_list_ip_set_expired = http_clean_results_obj['block_list_ip_set_expired']

        # Dedupe into new list
        block_list_ip_set_expired_deduped = list(set(block_list_ip_set_expired))

        LOGGER.info('================================ Http flood clean results ================================')

        for ip_address in block_list_ip_set_expired_deduped:
            # pylint: disable=W1202
            LOGGER.info("Finding: Removed client ip: {0} from IP Set".format(ip_address))

        for ip_address in block_list_queue_expired:
            # pylint: disable=W1202
            LOGGER.info("Finding: Removed client ip: {0} from queue".format(ip_address))
