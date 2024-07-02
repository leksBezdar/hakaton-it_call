from abc import ABC
from dataclasses import dataclass


@dataclass
class BaseGetAllFilters(ABC):
    limit: int
    offset: int
