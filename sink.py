from abc import ABCMeta, abstractmethod


class Sink(metaclass=ABCMeta):

    @abstractmethod
    def flush(self, source):
        pass
