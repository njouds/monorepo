from app2.app.common.db import db
from app2.app.config import config
from commons.dependencies import get_db_session_dependency, get_redis_dependency
from fastapi import Depends

get_db_read_session = get_db_session_dependency(db.ReadSessionLocal)
db_read_session = Depends(get_db_read_session)

get_db_session = get_db_session_dependency(db.SessionLocal)
db_session = Depends(get_db_session)

get_redis_client = get_redis_dependency(config=config)
redis_client = Depends(get_redis_client)
