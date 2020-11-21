""" DynamoDB connection class """

import time
# pylint: disable=E0401
import boto3
from interfaces.iqueuedatabase import IQueueDatabase


class DynamoDBConnection(IQueueDatabase):
    """ Handles all connections to DynamoDB, implements interface IQueueDatabase """

    config_section_dynamoDB = 'DYNAMO_DB'

    def __init__(self, config):
        self.dynamodb = boto3.resource('dynamodb')

        # Get Dynamo DB table name
        self.dynamodb_block_list_table_name = config[self.config_section_dynamoDB]['BLOCK_LIST_QUEUE_TABLE']

    def insert_into_queue(self, client_list) -> None:
        """ Inserts bulk data into list queue table """

        put_item_request_list = []

        for alb_client in client_list:

            # Generate current timestamp
            timestamp_cur = int(time.time())

            # Generate uuid to conform to primary key restrictions
            uuid = alb_client.client_ip + '_' + str(timestamp_cur) + '_' + alb_client.http_flood_level.name

            # Add to put item request list
            put_item_request_list.append({
                'PutRequest' : {
                    'Item' : {
                        'uuid': uuid,
                        'ip': alb_client.client_ip,
                        'flood_level': alb_client.http_flood_level.name,
                        'timestamp_start': timestamp_cur
                    }
                }
            })

        # Divide put_item_request_list into chunks of smaller list because bulk_insert limit is 25 per request:
        put_item_request_chunks_list = [put_item_request_list[x:x+25] for x in range(0, len(put_item_request_list), 25)]

        for put_item_request_chunk in put_item_request_chunks_list:
            self.dynamodb.batch_write_item(RequestItems={
                self.dynamodb_block_list_table_name: put_item_request_chunk
            })

    def get_from_queue(self) -> list:
        """ Retrieves all entries from the block-list queue """

        table_block_list_queue = self.dynamodb.Table(self.dynamodb_block_list_table_name)

        # Return all entries from database
        block_list_entries = table_block_list_queue.scan()

        return block_list_entries

    def remove_from_queue(self, client_list) -> None:
        """ Removes an item from the block-list queue by a given list of uuid's """

        uuid_list_expired = client_list  # Rename from implementation
        uuid_list_expired_commands = []

        for uuid in uuid_list_expired:
            uuid_list_expired_commands.append({
                'DeleteRequest': {
                    'Key': {
                        'uuid': uuid
                    }
                }
            })

        # Divide put_item_request_list into chunks of smaller list because bulk_insert limit is 25 per request:
        uuid_list_expired_chunks = [uuid_list_expired_commands[x:x+25]
                                    for x in range(0, len(uuid_list_expired_commands), 25)]

        for uuid_list_expired_chunk in uuid_list_expired_chunks:
            self.dynamodb.batch_write_item(RequestItems={
                self.dynamodb_block_list_table_name: uuid_list_expired_chunk
            })
