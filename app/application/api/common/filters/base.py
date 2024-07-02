from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BaseGetAllFilters(ABC):
    limit: int
    offset: int

    @abstractmethod
    def to_infrastructure_filters(self): ...
