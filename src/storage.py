from abc import ABC, abstractmethod


class AbstractJson(ABC):
    @abstractmethod
    def read_data(self):
        pass

    @abstractmethod
    def add_date(self, data):
        pass

    @abstractmethod
    def delete_data(self, data):
        pass


class JsonSaver(AbstractJson):

    def __init__(self, filepath):
        self.__filepath = filepath

    def read_data(self):
