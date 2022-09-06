from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..exceptions import existenceException

from common.utils import hash_password
from app.api.user.models import User
from ..schemas import UserCreateRequest


def add_new_user_(
    body: UserCreateRequest,
    db_session: Session,
):

    db_session.add(
        User(
            first_name=body.first_name,
            hashed_password=hash_password(body.password),
            username=body.username,
        )
    )

    try:
        db_session.flush()
    except IntegrityError:
        raise existenceException
