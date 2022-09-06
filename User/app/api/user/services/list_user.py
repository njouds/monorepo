from sqlalchemy.orm import Session
from ..models import User
from sqlalchemy import select

def list_user_(session: Session):

    users: list[User]= session.execute(select(User)).scalars().all()
    return users

