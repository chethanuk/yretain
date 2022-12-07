"""Application implementation - ASGI."""
import logging

from fastapi import Depends, FastAPI

from fastapi_crudrouter import MemoryCRUDRouter as CRUDRouter
from gunicorn.util import getcwd
from fastapi.security import HTTPBasic, HTTPBasicCredentials


from yretain.app.models import Coupons, Customers, CustomersActivity, ReportFormat
from yretain.app.models.db import User, create_db_and_tables
from yretain.app.models.schemas import UserRead, UserCreate, UserUpdate
from yretain.app.models.users import fastapi_users, auth_backend, current_active_user
from yretain.config import settings
from yretain.app.router import root_api_router
from yretain.app.utils import RedisClient, AiohttpClient
from yretain.app.exceptions import (
    HTTPException,
    http_exception_handler,
)

log = logging.getLogger(__name__)


async def on_startup():
    """Define FastAPI startup event handler.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#startup-event

    """
    log.debug("Execute FastAPI startup event handler.")
    if settings.USE_REDIS:
        await RedisClient.open_redis_client()

    AiohttpClient.get_aiohttp_client()

    # Not needed if you set up a migration system like Alembic
    await create_db_and_tables()


async def on_shutdown():
    """Define FastAPI shutdown event handler.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#shutdown-event

    """
    log.debug("Execute FastAPI shutdown event handler.")
    # Gracefully close utilities.
    if settings.USE_REDIS:
        await RedisClient.close_redis_client()

    await AiohttpClient.close_aiohttp_client()


def get_application():
    """Initialize FastAPI application.

    Returns:
       FastAPI: Application object instance.

    """
    log.debug("Initialize FastAPI application node.")
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
    )
    log.debug("Add application routes.")
    app.include_router(root_api_router)
    log.debug("Register global exception handler for custom HTTPException.")
    app.add_exception_handler(HTTPException, http_exception_handler)


    app.include_router(
        fastapi_users.get_auth_router(auth_backend, requires_verification=False),
        prefix="/auth/jwt", tags=["auth"]
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )

    app.include_router(CRUDRouter(schema=Coupons, paginate=10),
                       dependencies=[Depends(current_active_user)])
    app.include_router(CRUDRouter(schema=Customers, paginate=10),
                       dependencies=[Depends(current_active_user)])
    app.include_router(CRUDRouter(schema=CustomersActivity, paginate=10),
                       dependencies=[Depends(current_active_user)])

    @app.post("/gen_report/", dependencies=[Depends(current_active_user)])
    async def create_report(report: ReportFormat):
        return report

    # launch_ui(getcwd(), "8501")
    security = HTTPBasic()

    # @app.get("/users/me")
    # def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    #     return {"username": credentials.username, "password": credentials.password}

    @app.get("/authenticated-route")
    async def authenticated_route(user: User = Depends(current_active_user)):
        return {"message": f"Hello {user.email}!"}

    return app

