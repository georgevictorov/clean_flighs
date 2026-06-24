from flights.service_layer.uow import AbstractUnitOfWork
from flights.infrastructure.repo.memory.memory_repository import InMemoryRepository


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.flights = InMemoryRepository()
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
