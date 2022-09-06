from Courses.app.common.dependencies import db_session
from fastapi import APIRouter
from sqlalchemy.orm import Session

from .schemas import coursesResponse
from .services.list_courses import list_courses_

courses_router = APIRouter(prefix="/courses", tags=["courses"])


@courses_router.get(
    path="",
    response_model=list[coursesResponse],
)
def list_courses(
    session: Session = db_session,
):
    return list_courses_(session=session)
