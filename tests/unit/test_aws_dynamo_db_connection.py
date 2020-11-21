""" Unit test for DynamoDBConnection class """

import os
import sys
import inspect
# pylint: disable=E0401
import pytest

# Fix module import form parent directory error.
# Reference: https://stackoverflow.com/questions/55933630/
# python-import-statement-modulenotfounderror-when-running-tests-and-referencing
CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT_SRC = "%s/LambdaCode" % os.path.dirname(PROJECT_ROOT)

# Set up sys path
sys.path.insert(0, PROJECT_ROOT_SRC)

# Import project classes
# pylint: disable=C0413
# pylint: disable=W0621
from LambdaCode.connection.aws_dynamodb_connection import DynamoDBConnection
from tests.unit.helper.shared_classes import ALBClient, HTTPFloodLevel


@pytest.fixture(autouse=True)
def cleanup_dynamodb(get_mock_config):
    """ Cleans up block list queue table before each unit test """

    # Get entries in DynamoDB table
    dynamodb_response = DynamoDBConnection(get_mock_config).get_from_queue()
    block_list_queue_entries = dynamodb_response['Items']

    # Create list of uuid's to be removed
    uuid_list = [item['uuid'] for item in block_list_queue_entries]

    # Remove all items
    DynamoDBConnection(get_mock_config).remove_from_queue(uuid_list)


def test_insert_into_queue(get_mock_config):
    """ Test insert_into_queue method from the DynamoDBConnection class """

    # !ARRANGE!
    alb_client_1 = ALBClient('1.1.1.1', 1001, HTTPFloodLevel.flood_level_low)
    alb_client_2 = ALBClient('2.2.2.2', 5001, HTTPFloodLevel.flood_level_medium)
    alb_client_3 = ALBClient('3.3.3.3', 10001, HTTPFloodLevel.flood_level_critical)

    alb_client_list = [alb_client_1, alb_client_2, alb_client_3]

    # !ACT!
    DynamoDBConnection(get_mock_config).insert_into_queue(alb_client_list)

    # !ASSERT!
    dynamodb_response = DynamoDBConnection(get_mock_config).get_from_queue()

    block_list_queue_entries = dynamodb_response['Items']

    # Assert number is equal to entries we just created
    assert len(block_list_queue_entries) == 3

    client_1_is_present = False
    client_2_is_present = False
    client_3_is_present = False

    # Assert each item property has the right value
    for block_list_queue_entry in block_list_queue_entries:

        if block_list_queue_entry['ip'] == '1.1.1.1':
            client_1_is_present = True
            assert block_list_queue_entry['flood_level'] == 'flood_level_low'
            assert str(block_list_queue_entry['uuid']).startswith('1.1.1.1')

        elif block_list_queue_entry['ip'] == '2.2.2.2':
            client_2_is_present = True
            assert block_list_queue_entry['flood_level'] == 'flood_level_medium'
            assert str(block_list_queue_entry['uuid']).startswith('2.2.2.2')

        elif block_list_queue_entry['ip'] == '3.3.3.3':
            client_3_is_present = True
            assert block_list_queue_entry['flood_level'] == 'flood_level_critical'
            assert str(block_list_queue_entry['uuid']).startswith('3.3.3.3')

    # Assert all clients are present
    assert client_1_is_present
    assert client_2_is_present
    assert client_3_is_present
