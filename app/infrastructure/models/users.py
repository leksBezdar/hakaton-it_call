from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import TIMESTAMP, Null, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infrastructure.models.common.base import Base, BaseIDMixin


class UserModel(Base, BaseIDMixin):
    __mapper_args__: ClassVar[dict[Any, Any]] = {"eager_defaults": True}

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    is_subscribed: Mapped[bool] = mapped_column(
        default=False, server_default=text("false")
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False, server_default=text("false")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        default=None, server_default=Null()
    )

    def __str__(self):
        return self.username
