from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from .config import CommonBaseConfig


def set_up_main(config: CommonBaseConfig, routers_modules: list = []):
    app = FastAPI(
        debug=not config.production,
        title=f"{config.APP_NAME}({config.ENVIRONMENT}-{config.RELEASE_SHA})",
        openapi_url=config.openapi_url,
        docs_url=config.docs_url,
    )

    app.add_middleware(GZipMiddleware)
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=config.FORWARDED_ALLOW_IPS)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.allow_hosts)
    app.add_middleware(CORSMiddleware, allow_origins=config.allow_core_origins)

    for router_module in routers_modules:
        app.include_router(router_module)

    # for nested routes docs
    for path_k, path_v in app.openapi()["paths"].items():
        for method_k, method_v in path_v.items():
            if len(method_v["tags"]) > 1:
                method_v["tags"] = [method_v["tags"][-1]]

    return app
