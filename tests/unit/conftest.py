""" This is a shared module for all unit tests. This sets up all shared fixtures at session scope level """

# pylint: disable=E0401
import pytest

@pytest.fixture(scope="session")
def get_mock_config():
    """ Return the mocked config parser with arbitrary values of the components to be tested """

    # Create HTTP Flood config section
    config_section_http_flood_detection = {'HTTP_FLOOD_LOW_LEVEL_THRESHOLD': 1000,
                                           'HTTP_FLOOD_MEDIUM_LEVEL_THRESHOLD': 5000,
                                           'HTTP_FLOOD_CRITICAL_LEVEL_THRESHOLD': 10000
                                           }
    # Create AWS WAF Config section
    config_section_aws_waf = {'IP_SET_BLOCKED_NAME': 'ip_set_blocked_test',
                              'IP_SET_BLOCKED_SCOPE': 'REGIONAL',
                              'IP_SET_BLOCKED_IDENTIFIER': '15d93a77-4031-4c0e-8744-3f8e21b15751'
                              }

    # Create DynamoDB config section
    config_section_dynamo_db = {'BLOCK_LIST_QUEUE_TABLE': 'block_list_queue_test'}

    # Mock Config parser
    mock_config = {'HTTP_FLOOD_DETECTION': config_section_http_flood_detection,
                   'AWS_WAF': config_section_aws_waf,
                   'DYNAMO_DB': config_section_dynamo_db
                   }

    return mock_config
