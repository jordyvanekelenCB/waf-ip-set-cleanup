""" DynamoDB connection class """

# pylint: disable=E0401
import boto3
from interfaces import IQueueDatabase


class DynamoDBConnection(IQueueDatabase):
    """ Handles all connections to DynamoDB, implements interface IQueueDatabase """

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

    def get_from_queue(self) -> list:
        """ Retrieves all entries from the block-list queue """

        table_block_list_queue = self.dynamodb.Table('block_list_queue')

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
                'block_list_queue': uuid_list_expired_chunk
            })

    def insert_into_queue(self, client_list) -> None:
        pass
