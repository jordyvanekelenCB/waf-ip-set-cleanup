""" Unit test containing tests for HTTP Flood Clean class """

import sys
import os
import inspect
import configparser
import time
# pylint: disable=E0401
import pytest


# Fix module import form parent directory error.
# Reference: https://stackoverflow.com/questions/55933630/
# python-import-statement-modulenotfounderror-when-running-tests-and-referencing
CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT_SRC = "%s/LambdaCode" % os.path.dirname(PROJECT_ROOT)

# Set up configuration path
CONFIG_PATH = os.path.join(os.path.dirname(PROJECT_ROOT_SRC + "/LambdaCode"), 'config', 'config.ini')

# Set up sys path
sys.path.insert(0, PROJECT_ROOT_SRC)

# Import project classes
# pylint: disable=C0413
from http_flood_clean import HTTPFloodClean


@pytest.fixture()
def setup_config():
    """ Fixture for setting up configuration parser """

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    return config

# pylint: disable=W0621
# pylint: disable=R0914
def test_filter_block_list_queue(setup_config):
    """ This method tests the filter_block_list_queue method """

    # !ARRANGE!
    http_flood_clean = HTTPFloodClean(setup_config)

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    # Get timestamps of http floods
    http_flood_low_expire_in_seconds = int(config['HTTP_FLOOD_CLEAN']['HTTP_FLOOD_LOW_LEVEL_TIMEOUT']) * 60
    http_flood_medium_expire_in_seconds = int(config['HTTP_FLOOD_CLEAN']['HTTP_FLOOD_MEDIUM_LEVEL_TIMEOUT']) * 60
    http_flood_critical_expire_in_seconds = int(config['HTTP_FLOOD_CLEAN']['HTTP_FLOOD_CRITICAL_LEVEL_TIMEOUT']) * 60

    # Generate expired timestamps, remove 1 minute so they are expired because there starting time is earlier
    http_flood_low_expired = int(time.time()) - http_flood_low_expire_in_seconds - 60
    http_flood_medium_expired = int(time.time()) - http_flood_medium_expire_in_seconds - 60
    http_flood_critical_expired = int(time.time()) - http_flood_critical_expire_in_seconds - 60

    # Generate non-expired timestamp, add 1 minute so it is not expired
    http_flood_critical_not_expired = int(time.time()) - http_flood_critical_expire_in_seconds + 60

    # Create UUID's
    block_list_item_low_expired_1111_uuid = '1.1.1.1_' + str(http_flood_low_expired) + '_flood_level_low'
    block_list_item_medium_expired_2222_uuid = '2.2.2.2_' + str(http_flood_medium_expired) + '_flood_level_medium'
    block_list_item_critical_expired_3333_uuid = '3.3.3.3_' + str(http_flood_low_expired) + '_flood_level_critical'
    block_list_item_critical_not_expired_1111_uuid = '1.1.1.1_' + str(http_flood_critical_not_expired)  \
                                                     + '_flood_level_critical'

    # Create block list items
    block_list_item_low_expired_1111 = {'ip': '1.1.1.1', 'timestamp_start': http_flood_low_expired,
                                        'uuid': block_list_item_low_expired_1111_uuid,
                                        'flood_level': 'flood_level_low'}
    block_list_item_medium_expired_2222 = {'ip': '2.2.2.2', 'timestamp_start': http_flood_medium_expired,
                                           'uuid': block_list_item_medium_expired_2222_uuid,
                                           'flood_level': 'flood_level_medium'}
    block_list_item_critical_expired_3333 = {'ip': '3.3.3.3', 'timestamp_start': http_flood_critical_expired,
                                             'uuid': block_list_item_critical_expired_3333_uuid,
                                             'flood_level': 'flood_level_critical'}
    block_list_item_critical_not_expired_1111 = {'ip': '1.1.1.1', 'timestamp_start': http_flood_critical_not_expired,
                                                 'uuid': block_list_item_critical_not_expired_1111_uuid,
                                                 'flood_level': 'flood_level_critical'}

    # Add items to block list queue
    block_list_queue = {'Items': []}

    block_list_queue['Items'].append(block_list_item_low_expired_1111)
    block_list_queue['Items'].append(block_list_item_medium_expired_2222)
    block_list_queue['Items'].append(block_list_item_critical_expired_3333)
    block_list_queue['Items'].append(block_list_item_critical_not_expired_1111)

    # !ACT!
    http_clean_results_obj = http_flood_clean.filter_block_list_queue(block_list_queue)

    block_list_queue_expired = http_clean_results_obj['block_list_queue_expired']
    block_list_ip_set_expired = http_clean_results_obj['block_list_ip_set_expired']

    # !ASSERT!

    # Assert that there are three items in queue, because three have been expired
    assert len(block_list_queue_expired) == 3

    # Assert that there are 2 items in ip set, because only two have been fully expired have been expired
    assert len(block_list_ip_set_expired) == 2

    # Assert UUID's in list queue are as expected
    assert block_list_queue_expired[0] == block_list_item_low_expired_1111_uuid
    assert block_list_queue_expired[1] == block_list_item_medium_expired_2222_uuid
    assert block_list_queue_expired[2] == block_list_item_critical_expired_3333_uuid

    # Assert IP addresses in ip set are as expected
    assert block_list_ip_set_expired[0] == '2.2.2.2' + '/32'
    assert block_list_ip_set_expired[1] == '3.3.3.3' + '/32'
