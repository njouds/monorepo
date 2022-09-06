from sqlalchemy.orm import Session


def list_user_(session: Session):

    users=session.query(User).all()
    return []
