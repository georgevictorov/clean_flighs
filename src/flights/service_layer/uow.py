from abc import ABC, abstractmethod
from flights.service_layer.repository import AbstractRepository


class AbstractUnitOfWork(ABC):
    flights: AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError
