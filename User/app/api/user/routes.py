from fastapi.security import HTTPBearer
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.common.dependencies import db_session,get_verified_current_user_or_none
from services.add_user import add_new_user_
from services.list_user import list_user_
from services.login_user import login_
from services.update_user import update_user_
from models import User

from .schemas import (
    PublicUserResponse,
    UserCreateRequest,
    UserLoginResponse,
    UserLoginRequest,
    UserResponse,
    UserUpdateRequest,
)

# from .services.list_courses import list_courses_

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get(
    path="",
    response_model=list[PublicUserResponse],
)
def list_users(session: Session = db_session):
    """
    list all of the users , returning public data only
    """
    return list_user_(session=session)


@user_router.post(
    path="",
    responses={
        status.HTTP_200_OK: {"description": "user created successfully", "model": UserResponse},
        status.HTTP_409_CONFLICT: {"description": "the username is already used"},
    },
)
def signup_a_new_user(body: UserCreateRequest, session: Session = db_session):
    """
    using this endpoint the user will register a new account,
    """
    return add_new_user_(body, session)


@user_router.post(
    path="/login",
    responses={
        status.HTTP_200_OK: {"description": "valid credentials", "model": UserLoginResponse},
        status.HTTP_401_UNAUTHORIZED: {"description": "invalid credentials"},
    },
)
def login(
    body: UserLoginRequest, session: Session = db_session
):
    """
    using this endpoint the user will try to login with their username/password,
    """
    return login_(body, session)


@user_router.get(
    path="/me",
    response_model=UserResponse
)
def get_current_user_data(current: UserResponse = Depends(get_verified_current_user_or_none) ,session: Session = db_session ):
    """
    get the current user data
    """

    user=session.query(User).filter_by(id=current.id)

    return UserResponse(user.id )

@user_router.patch(
    path="/",
    response_model=UserResponse,
    
)
def update_current_user_data(body: UserUpdateRequest,session: Session = db_session,current: UserResponse = Depends(get_verified_current_user_or_none)):
    """
    update the current user data, if the key is not passed ,, it must be ignored
    """
    return update_user_(body,session,current)
