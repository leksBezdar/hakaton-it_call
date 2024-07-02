from typing import Annotated
from punq import Container
from fastapi import APIRouter, Depends, HTTPException, Response, status

from application.api.schemas import SErrorMessage
from application.api.users.filters import GetUsersFilters
from application.api.users.schemas import (
    SChangePassword,
    SChangeUsername,
    SCreateUserIn,
    SCreateUserOut,
    SGetUser,
    SGetUsersQueryResponse,
    SLoginIn,
    SLoginOut,
)
from domain.entities.users import UserEntity
from domain.exceptions.base import ApplicationException
from logic.commands.users import (
    ChangePasswordCommand,
    ChangeUsernameCommand,
    CreateUserCommand,
    DeleteUserCommand,
    RestoreUserCommand,
    SubscribeToEmailSenderCommand,
    UnsubscribeFromEmailSenderCommand,
    UserLoginCommand,
)
from logic.init import init_container
from logic.mediator.base import Mediator
from logic.queries.users import (
    GetTokensQuery,
    GetUserByIdQuery,
    GetUserByUsernameQuery,
    GetUsersQuery,
    Tokens,
)
from settings.settings import Settings


user_router = APIRouter()


@user_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": SCreateUserOut},
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def create_user(
    user_in: SCreateUserIn,
    container: Annotated[Container, Depends(init_container)],
) -> SCreateUserOut:
    """Create new user."""
    mediator: Mediator = container.resolve(Mediator)

    try:
        user, *_ = await mediator.handle_command(
            CreateUserCommand(
                email=user_in.email,
                username=user_in.username,
                password=user_in.password,
                is_subscribed=user_in.is_subscribed,
            )
        )
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    return SCreateUserOut.from_entity(user)


@user_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": SLoginOut},
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def login(
    user_in: SLoginIn,
    container: Annotated[Container, Depends(init_container)],
    response: Response,
):
    """Login user."""
    mediator: Mediator = container.resolve(Mediator)
    settings: Settings = container.resolve(Settings)

    try:
        user, *_ = await mediator.handle_command(
            UserLoginCommand(username=user_in.username, password=user_in.password)
        )
        user: UserEntity

    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    else:
        # TODO change get tokens query to get tokens command then add /refresh_tokens router
        tokens: Tokens = await mediator.handle_query(GetTokensQuery(user_oid=user.oid))
        response.set_cookie(
            "access_token",
            tokens.access_token,
            max_age=settings.access_token_expire_minutes * 60,
        )
        response.set_cookie(
            "refresh_token",
            tokens.refresh_token,
            max_age=settings.refresh_token_expire_days * 60 * 24,
        )

    return SLoginOut.from_entity(user)


@user_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": SGetUsersQueryResponse},
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def get_all_users(
    container: Annotated[Container, Depends(init_container)],
    filters: GetUsersFilters = Depends(),
) -> SGetUsersQueryResponse:
    """Get all users from specified group."""
    mediator: Mediator = container.resolve(Mediator)

    try:
        users, count = await mediator.handle_query(
            GetUsersQuery(filters=filters.to_infrastructure_filters())
        )
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    return SGetUsersQueryResponse(
        count=count,
        limit=filters.limit,
        offset=filters.offset,
        items=[SGetUser.from_entity(user) for user in users],
    )


@user_router.get(
    "/{user_oid}/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": SGetUser},
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def get_user_by_id(
    user_oid: str,
    container: Annotated[Container, Depends(init_container)],
):
    """Get user by id."""
    mediator: Mediator = container.resolve(Mediator)
    try:
        user = await mediator.handle_query(GetUserByIdQuery(user_oid=user_oid))
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    return SGetUser.from_entity(user)


@user_router.get(
    "/@{username}/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": SGetUser},
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def get_user_by_username(
    username: str,
    container: Annotated[Container, Depends(init_container)],
):
    """Get user by username."""
    mediator: Mediator = container.resolve(Mediator)
    try:
        user = await mediator.handle_query(GetUserByUsernameQuery(username=username))
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    return SGetUser.from_entity(user)


@user_router.patch(
    "/{user_oid}/username/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def change_username(
    user_oid: str,
    user_in: SChangeUsername,
    container: Annotated[Container, Depends(init_container)],
):
    mediator: Mediator = container.resolve(Mediator)

    try:
        await mediator.handle_command(
            ChangeUsernameCommand(
                user_oid=user_oid,
                new_username=user_in.new_username,
            )
        )
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@user_router.patch(
    "/{user_oid}/password/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def change_password(
    user_oid: str,
    user_in: SChangePassword,
    container: Annotated[Container, Depends(init_container)],
):
    mediator: Mediator = container.resolve(Mediator)

    try:
        await mediator.handle_command(
            ChangePasswordCommand(
                user_oid=user_oid,
                old_password=user_in.old_password,
                new_password=user_in.new_password,
            )
        )
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@user_router.patch(
    "/{user_oid}/subscribe",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def subscribe_to_email_sender(
    user_oid: str,
    container: Annotated[Container, Depends(init_container)],
):
    mediator: Mediator = container.resolve(Mediator)

    try:
        await mediator.handle_command(SubscribeToEmailSenderCommand(user_oid=user_oid))
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@user_router.patch(
    "/{user_oid}/unsubscribe",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def unsubscribe_from_email_sender(
    user_oid: str,
    container: Annotated[Container, Depends(init_container)],
):
    mediator: Mediator = container.resolve(Mediator)

    try:
        await mediator.handle_command(
            UnsubscribeFromEmailSenderCommand(user_oid=user_oid)
        )
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@user_router.patch(
    "/{user_oid}/restore/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def restore_user(
    user_oid: str,
    container: Annotated[Container, Depends(init_container)],
):
    mediator: Mediator = container.resolve(Mediator)

    try:
        await mediator.handle_command(RestoreUserCommand(user_oid=user_oid))
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@user_router.delete(
    "/{user_oid}/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SErrorMessage},
    },
)
async def delete_user(
    user_oid: str,
    container: Annotated[Container, Depends(init_container)],
) -> None:
    """Delete user."""
    mediator: Mediator = container.resolve(Mediator)

    try:
        await mediator.handle_command(DeleteUserCommand(user_oid=user_oid))
    except ApplicationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
