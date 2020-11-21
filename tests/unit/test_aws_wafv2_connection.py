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

from LambdaCode.connection.aws_wafv2_connection import AWSWAFv2Connection


@pytest.fixture(autouse=True)
def cleanup_wafv2(get_mock_config):
    """ Cleans up Waf IP Set before each unit test """

    # Get locktoken from WAFv2
    wafv2_response = AWSWAFv2Connection(get_mock_config).retrieve_ip_set()
    locktoken = wafv2_response['LockToken']

    # Update IP set with empty list
    AWSWAFv2Connection(get_mock_config).update_ip_set([], locktoken)


def test_wafv2(get_mock_config):
    """ Test both the retrieve_ip_set and update_ip_set method from the WAFv2Connection class """

    # !ARRANGE!

    # Get locktoken from WAFv2
    wafv2_response = AWSWAFv2Connection(get_mock_config).retrieve_ip_set()
    locktoken = wafv2_response['LockToken']

    ip_set_addresses = ['1.1.1.1/32', '2.2.2.2/32', '3.3.3.3/32']
    AWSWAFv2Connection(get_mock_config).update_ip_set(ip_set_addresses, locktoken)

    # !ACT!
    wafv2_response = AWSWAFv2Connection(get_mock_config).retrieve_ip_set()

    # !ASSERT!
    block_list_entries = wafv2_response["IPSet"]["Addresses"]

    assert len(wafv2_response) == 3

    client_1_is_present = False
    client_2_is_present = False
    client_3_is_present = False

    for block_list_entry in block_list_entries:
        if block_list_entry == '1.1.1.1/32':
            client_1_is_present = True
        if block_list_entry == '2.2.2.2/32':
            client_2_is_present = True
        if block_list_entry == '3.3.3.3/32':
            client_3_is_present = True

    # Assert all items are present in block list
    assert client_1_is_present
    assert client_2_is_present
    assert client_3_is_present
