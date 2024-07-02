from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar
from uuid import uuid4


@dataclass
class BaseEvent(ABC):
    event_id: str = field(default_factory=lambda: str(uuid4()), kw_only=True)

    title: ClassVar[str]
    occured_at: datetime = field(
        default_factory=lambda: datetime.now(UTC), kw_only=True
    )
