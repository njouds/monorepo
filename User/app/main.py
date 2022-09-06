from commons.main import set_up_main

from .api.user.routes import user_router
from .config import config

app = set_up_main(
    config,
    routers_modules=[
        user_router,
    ],
)
