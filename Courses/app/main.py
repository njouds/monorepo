from commons.main import set_up_main

from .api.courses.routes import courses_router
from .config import config

app = set_up_main(
    config,
    routers_modules=[
        courses_router,
    ],
)
