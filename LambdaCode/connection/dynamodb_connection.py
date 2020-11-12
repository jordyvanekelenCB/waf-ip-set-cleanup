""" DynamoDB connection class """

import time

# pylint: disable=E0401
import boto3


class DynamoDBConnection:
    """ Handles all connections to DynamoDB """

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

    def insert_block_list_queue_entry(self, ip_address, flood_level):
        """ Inserts entry in block-list queue """

        table_block_list_queue = self.dynamodb.Table('block_list_queue')

        # Generate current timestamp
        timestamp_cur = int(time.time())

        # Generate uuid to conform to primary key restrictions
        uuid = ip_address + '_' + str(timestamp_cur) + '_' + flood_level

        # Insert item and get response
        table_block_list_queue.put_item(Item={
            'uuid': uuid,
            'ip': ip_address,
            'flood_level': flood_level,
            'timestamp_start': timestamp_cur
        })

    def retrieve_block_list_queue(self):
        """ Retrieves all entries from the block-list queue """

        table_block_list_queue = self.dynamodb.Table('block_list_queue')

        # Return all entries from database
        block_list_entries = table_block_list_queue.scan()

        return block_list_entries

    def remove_items_block_list_queue(self, uuid_list_expired):
        """ Removes an item from the block-list queue by a given list of uuid's """

        table_block_list_queue = self.dynamodb.Table('block_list_queue')

        for uuid in uuid_list_expired:
            table_block_list_queue.delete_item(Key={
                'uuid': uuid
            })
