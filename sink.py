from abc import ABCMeta, abstractmethod


class Sink(metaclass=ABCMeta):

    @abstractmethod
    def flush(self, source):
        pass

    @abstractmethod
    def insert_crash(self, source, linenum, type, info):
        pass
