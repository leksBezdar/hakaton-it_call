from dataclasses import field, dataclass
from datetime import UTC, datetime

from domain.entities.base import BaseEntity
from domain.exceptions.users import UserAlreadyDeleted, UserNotDeleted
from domain.values.users import Username, UserEmail
from domain.events.users import (
    RestoreUserEvent,
    UserChangedUsernameEvent,
    UserCreatedEvent,
    UserDeletedEvent,
    UserSubscribedToEmailSenderEvent,
    UserUnsubscribedFromEmailSenderEvent,
)


@dataclass(eq=False)
class UserEntity(BaseEntity):
    email: UserEmail
    username: Username
    is_subscribed: bool = field(default=False, kw_only=True)
    is_deleted: bool = field(default=False, kw_only=True)
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC), kw_only=True
    )
    deleted_at: datetime | None = field(default=None, kw_only=True)

    @classmethod
    async def create(
        cls,
        username: Username,
        email: UserEmail,
        is_subscribed: bool,
    ) -> "UserEntity":
        new_user = cls(
            email=email,
            username=username,
            is_subscribed=is_subscribed,
        )
        new_user.register_event(
            UserCreatedEvent(
                username=new_user.username.as_generic_type(),
                email=new_user.email.as_generic_type(),
                user_oid=new_user.oid,
                is_subscribed=new_user.is_subscribed,
            )
        )
        return new_user

    async def change_username(self, new_username: Username) -> None:
        self._validate_not_deleted()
        old_username = self.username
        self.username = new_username

        self.register_event(
            UserChangedUsernameEvent(
                user_oid=self.oid,
                old_username=old_username,
                new_username=new_username,
            )
        )

    async def subscribe_to_email_sender(self) -> None:
        self._validate_not_deleted()
        self.is_subscribed = True

        self.register_event(
            UserSubscribedToEmailSenderEvent(
                user_oid=self.oid,
                username=self.username.as_generic_type(),
                email=self.email.as_generic_type(),
            )
        )

    async def unsubscribe_from_email_sender(self) -> None:
        self._validate_not_deleted()
        self.is_subscribed = False

        self.register_event(
            UserUnsubscribedFromEmailSenderEvent(
                user_oid=self.oid,
                username=self.username.as_generic_type(),
                email=self.email.as_generic_type(),
            )
        )

    async def restore(self) -> None:
        self._validate_deleted()
        self.is_deleted = False
        self.deleted_at = None

        self.register_event(
            RestoreUserEvent(
                user_oid=self.oid,
                username=self.username.as_generic_type(),
                restore_datetime=datetime.now(UTC),
            )
        )

    async def delete(self) -> None:
        self._validate_not_deleted()
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)

        self.register_event(
            UserDeletedEvent(
                user_oid=self.oid,
                username=self.username.as_generic_type(),
                email=self.email.as_generic_type(),
            )
        )

    def _validate_not_deleted(self) -> None:
        if self.is_deleted:
            raise UserAlreadyDeleted(self.oid)

    def _validate_deleted(self) -> None:
        if not self.is_deleted:
            raise UserNotDeleted(self.oid)
