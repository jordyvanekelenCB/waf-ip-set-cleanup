""" File containing HTTP Flood Clean class """

import time
from connection.aws_dynamodb_connection import DynamoDBConnection
from connection.aws_wafv2_connection import AWSWAFv2Connection


class HTTPFloodClean:
    """ This class is responsible for updating the block list queue and IP set block list """

    config_section_http_flood_clean = 'HTTP_FLOOD_CLEAN'

    def __init__(self, config):
        self.config = config

        self.http_flood_low_level_timeout = int(self.config[self.config_section_http_flood_clean]
                                                ['HTTP_FLOOD_LOW_LEVEL_TIMEOUT'])
        self.http_flood_medium_level_timeout = int(self.config[self.config_section_http_flood_clean]
                                                   ['HTTP_FLOOD_MEDIUM_LEVEL_TIMEOUT'])
        self.http_flood_critical_level_timeout = int(self.config[self.config_section_http_flood_clean]
                                                     ['HTTP_FLOOD_CRITICAL_LEVEL_TIMEOUT'])

    def clean_http_flood(self):
        """ Main function """

        block_list_queue = self.retrieve_blocklist_queue(self.config)

        block_list_expired_obj = self.filter_block_list_queue(block_list_queue)
        block_list_queue_expired = block_list_expired_obj['block_list_queue_expired']
        block_list_ip_set_expired = block_list_expired_obj['block_list_ip_set_expired']

        self.remove_items_from_block_list(block_list_queue_expired, block_list_ip_set_expired)

        return block_list_expired_obj

    @staticmethod
    def retrieve_blocklist_queue(config):
        """ Retrieve the block list queue from database """

        # Get block list entries to be removed
        block_list_queue = DynamoDBConnection(config).get_from_queue()

        return block_list_queue

    def filter_block_list_queue(self, block_list_queue):
        """ Filter the block list queue and return a dictionary with two lists. The first
        list (block_list_queue_expired) is a list of items that need to be removed from the queue.
        The second list (block_list_ip_set_expired) is a list of items that need to be removed
        from the IP set block list"""

        block_list_queue_items = block_list_queue["Items"]

        block_list_queue_expired = [] # List of uuids for database
        block_list_ip_set_expired_temp = [] # Temporary list to check duplicates against
        block_list_ip_set_not_expired = []  # List of ips for wafv2

        for item in block_list_queue_items:

            timestamp_start = int(item['timestamp_start'])
            flood_level = item['flood_level']

            if flood_level == 'flood_level_low':
                if int(time.time()) > timestamp_start + self.http_flood_low_level_timeout * 60:
                    block_list_queue_expired.append(item['uuid'])
                    block_list_ip_set_expired_temp.append(item['ip'] + '/32')
                else:
                    block_list_ip_set_not_expired.append(item['ip'] + '/32')
                    continue
            elif flood_level == 'flood_level_medium':
                if int(time.time()) > timestamp_start + self.http_flood_medium_level_timeout * 60:
                    block_list_queue_expired.append(item['uuid'])
                    block_list_ip_set_expired_temp.append(item['ip'] + '/32')
                else:
                    block_list_ip_set_not_expired.append(item['ip'] + '/32')
                    continue
            elif flood_level == 'flood_level_critical':
                if int(time.time()) > timestamp_start + self.http_flood_critical_level_timeout * 60:
                    block_list_queue_expired.append(item['uuid'])
                    block_list_ip_set_expired_temp.append(item['ip'] + '/32')

                else:
                    block_list_ip_set_not_expired.append(item['ip'] + '/32')
                    continue

        # block_list_ip_set_expired = block_list_ip_set_expired_temp - block_list_ip_set_not_expired
        block_list_ip_set_expired = [ip for ip in block_list_ip_set_expired_temp if ip not in block_list_ip_set_not_expired]

        return {'block_list_queue_expired': block_list_queue_expired, 'block_list_ip_set_expired': block_list_ip_set_expired}

    def remove_items_from_block_list(self, block_list_queue_expired, block_list_ip_set_expired):
        """ Call database methods to remove items from block list queue and from block list expired """

        # Get IP set, then update IP Set
        aws_waf_v2_helper = AWSWAFv2Connection(self.config)
        ip_set_response = aws_waf_v2_helper.retrieve_ip_set()

        current_blocklist = ip_set_response["IPSet"]["Addresses"]
        locktoken = ip_set_response["LockToken"]

        # New blocklist is current_blocklist - ips_to_be_removed
        new_blocklist = [ip for ip in current_blocklist if ip not in block_list_ip_set_expired]

        # Update current IP Set with new blocklist
        aws_waf_v2_helper.update_ip_set(new_blocklist, locktoken)

        # Remove removed items from database queue
        DynamoDBConnection(self.config).remove_from_queue(block_list_queue_expired)
