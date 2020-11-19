""" This module contains the IQueueDatabase class """

from abc import abstractmethod


class IQueueDatabase:
    """ This is an interface that exposes the database functions that are used for the queue database """

    @abstractmethod
    def insert_into_queue(self, client_list):
        """ Insert items into queue given a list of clients """

    @abstractmethod
    def get_from_queue(self):
        """ Retrieve items from queue """

    @abstractmethod
    def remove_from_queue(self, client_list):
        """ Remove items from queue given a list of clients or ID's """
