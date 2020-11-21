""" Unit test for ALB Log parser class """

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
from LambdaCode import app
from LambdaCode.connection.aws_dynamodb_connection import DynamoDBConnection
from LambdaCode.connection.aws_wafv2_connection import AWSWAFv2Connection
from tests.unit.helper.shared_classes import ALBClient, HTTPFloodLevel

@pytest.fixture
def get_mock_config():
    """ Return the mocked config parser with arbitrary values of the components to be tested """

    # Create HTTP Flood config section
    config_section_http_flood_clean = {'HTTP_FLOOD_LOW_LEVEL_TIMEOUT': -1,
                                       'HTTP_FLOOD_MEDIUM_LEVEL_TIMEOUT' : -1,
                                       'HTTP_FLOOD_CRITICAL_LEVEL_TIMEOUT': 60}
    # Create AWS WAF Config section
    config_section_aws_waf = {'IP_SET_BLOCKED_NAME': 'ip_set_blocked_test',
                              'IP_SET_BLOCKED_SCOPE': 'REGIONAL',
                              'IP_SET_BLOCKED_IDENTIFIER': '15d93a77-4031-4c0e-8744-3f8e21b15751'
                              }

    # Create DynamoDB config section
    config_section_dynamo_db = {'BLOCK_LIST_QUEUE_TABLE': 'block_list_queue_test'}

    # Mock Config parser
    mock_config = {'HTTP_FLOOD_CLEAN': config_section_http_flood_clean,
                   'AWS_WAF': config_section_aws_waf,
                   'DYNAMO_DB': config_section_dynamo_db
                   }

    return mock_config


@pytest.fixture(autouse=True)
def cleanup_dynamodb(get_mock_config):
    """ Cleans up block list queue table before each integration test """

    # Get entries in DynamoDB table
    dynamodb_response = DynamoDBConnection(get_mock_config).get_from_queue()
    block_list_queue_entries = dynamodb_response['Items']

    # Create list of uuid's to be removed
    uuid_list = [item['uuid'] for item in block_list_queue_entries]

    # Remove all items
    DynamoDBConnection(get_mock_config).remove_from_queue(uuid_list)


@pytest.fixture(autouse=True)
def cleanup_wafv2(get_mock_config):
    """ Cleans up WAFv2 IP set before each integration test """

    # Get locktoken from WAFv2
    wafv2_response_lock = AWSWAFv2Connection(get_mock_config).retrieve_ip_set()
    locktoken = wafv2_response_lock['LockToken']

    # Update IP set with empty list
    AWSWAFv2Connection(get_mock_config).update_ip_set([], locktoken)


# pylint: disable=R0914
def test_integration(get_mock_config):
    """ Run integration test to make sure all AWS components are working together accordingly. External components that
     are being tested are S3, DynamoDB and Wafv2 """

    # !ARRANGE!

    # Create alb clients
    alb_client_1_1 = ALBClient('1.1.1.1', 1001, HTTPFloodLevel.flood_level_low)
    alb_client_1_2 = ALBClient('1.1.1.1', 10001, HTTPFloodLevel.flood_level_critical)
    alb_client_2 = ALBClient('2.2.2.2', 5001, HTTPFloodLevel.flood_level_medium)
    alb_client_3 = ALBClient('3.3.3.3', 10001, HTTPFloodLevel.flood_level_critical)

    # Create waf IP set
    waf_ip_set = ['1.1.1.1/32', '2.2.2.2/32', '3.3.3.3/32']

    alb_client_list = [alb_client_1_1, alb_client_1_2, alb_client_2, alb_client_3]

    # Insert items into DynamoDB queue table
    DynamoDBConnection(get_mock_config).insert_into_queue(alb_client_list)

    # Get locktoken from WAFv2
    wafv2_response_locktoken = AWSWAFv2Connection(get_mock_config).retrieve_ip_set()
    locktoken = wafv2_response_locktoken['LockToken']

    # Insert items into WAFv2 IP set
    AWSWAFv2Connection(get_mock_config).update_ip_set(waf_ip_set, locktoken)

    # Set the app.CONFIG to mocked config parser
    app.CONFIG = get_mock_config

    # !ACT!

    # Call entry point
    app.lambda_handler(None, None)

    # !ASSERT!

    # Retrieve item from DynamoDB
    dynamodb_response = DynamoDBConnection(get_mock_config).get_from_queue()
    block_list_queue_entries = dynamodb_response['Items']

    queue_list_client_1_is_present = False
    queue_list_client_3_is_present = False

    # Assert length of block list queue is two
    assert len(block_list_queue_entries) == 2

    # Assert items present have the right properties
    for block_list_queue_entry in block_list_queue_entries:

        if block_list_queue_entry['ip'] == '1.1.1.1':
            queue_list_client_1_is_present = True
            assert block_list_queue_entry['flood_level'] == 'flood_level_critical'
            assert str(block_list_queue_entry['uuid']).startswith('1.1.1.1')

        elif block_list_queue_entry['ip'] == '3.3.3.3':
            queue_list_client_3_is_present = True
            assert block_list_queue_entry['flood_level'] == 'flood_level_critical'
            assert str(block_list_queue_entry['uuid']).startswith('3.3.3.3')

    assert queue_list_client_1_is_present
    assert queue_list_client_3_is_present

    # Retrieve IP Set from WAFv2
    wafv2_response = AWSWAFv2Connection(get_mock_config).retrieve_ip_set()
    block_list_entries = wafv2_response["IPSet"]["Addresses"]

    # Assert length of IP set is two
    assert len(block_list_entries) == 2

    queue_list_client_1_is_present = False
    queue_list_client_3_is_present = False

    for block_list_queue_entry in block_list_entries:
        if block_list_queue_entry == '1.1.1.1/32':
            queue_list_client_1_is_present = True
        elif block_list_queue_entry == '3.3.3.3/32':
            queue_list_client_3_is_present = True

    # Assert items are present in IP set
    assert queue_list_client_1_is_present
    assert queue_list_client_3_is_present
