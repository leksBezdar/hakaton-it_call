from dataclasses import dataclass

from infrastructure.repositories.common.filters.base import BaseGetAllFilters


@dataclass
class GetUsersFilters(BaseGetAllFilters):
    limit: int = 10
    offset: int = 0
    show_deleted: bool = False
