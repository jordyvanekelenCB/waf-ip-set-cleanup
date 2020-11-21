""" This file contains classes to be shared among unit tests """

from enum import Enum

# pylint: disable=R0903
class ALBClient:
    """ This class acts as a model for ALBClient """

    def __init__(self, client_ip, number_of_requests, http_flood_level):

        self.client_ip = client_ip
        self.number_of_requests = number_of_requests
        self.http_flood_level = http_flood_level


class HTTPFloodLevel(Enum):
    """ Enum for HTTPFloodLevel """
    flood_level_none = 'flood_level_none'
    flood_level_low = 'flood_level_low'
    flood_level_medium = 'flood_level_medium'
    flood_level_critical = 'flood_level_critical'
