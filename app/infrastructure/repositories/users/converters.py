from domain.entities.users import UserEntity
from domain.values.users import UserEmail, UserTimezone, Username
from infrastructure.models.users import UserModel


def convert_user_entity_to_model(user: UserEntity) -> UserModel:
    return UserModel(
        oid=user.oid,
        email=user.email.as_generic_type(),
        username=user.username.as_generic_type(),
        user_timezone=user.user_timezone.as_generic_type(),
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_deleted=user.is_deleted,
        deleted_at=user.deleted_at,
        is_subscribed=user.is_subscribed,
    )


def convert_user_model_to_entity(user: UserModel) -> UserEntity:
    return UserEntity(
        oid=user.oid,
        email=UserEmail(value=user.email),
        username=Username(value=user.username),
        user_timezone=UserTimezone(value=user.user_timezone),
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
        is_deleted=user.is_deleted,
        is_subscribed=user.is_subscribed,
    )
