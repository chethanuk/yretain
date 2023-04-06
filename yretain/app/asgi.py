"""Application implementation - ASGI."""
import logging

from fastapi import Depends, FastAPI
from fastapi_crudrouter import DatabasesCRUDRouter

from yretain.app.exceptions import (
    HTTPException,
    http_exception_handler,
)
from yretain.app.models import Customers, ReportFormat
from yretain.app.models.coupons import coupons, CouponsCreate
from yretain.app.models.customer import customers, customers_activity, CustomersActivityCreate
from yretain.app.models.db import User, create_db_and_tables, database, metadata, \
    sync_engine
from yretain.app.models.schemas import UserRead, UserCreate, UserUpdate
from yretain.app.models.users import fastapi_users, auth_backend, current_active_user
from yretain.app.router import root_api_router
from yretain.app.utils import RedisClient, AiohttpClient
from yretain.config import settings

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

    # Establish the connection pool in AWS RDS MySQL
    await database.connect()

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

    # Close all connections in the connection pool in AWS RDS MySQL
    await database.disconnect()

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

    metadata.create_all(bind=sync_engine)

    app.include_router(DatabasesCRUDRouter(schema=CouponsCreate,
                                           create_schema=CouponsCreate,
                                           table=coupons,
                                           database=database,
                                           paginate=10),
                       dependencies=[Depends(current_active_user)])

    app.include_router(DatabasesCRUDRouter(schema=Customers,
                                           create_schema=Customers,
                                           table=customers,
                                           database=database,
                                           paginate=10),
                       dependencies=[Depends(current_active_user)])

    app.include_router(DatabasesCRUDRouter(schema=CustomersActivityCreate,
                                           create_schema=CustomersActivityCreate,
                                           table=customers_activity,
                                           database=database,
                                           paginate=10),
                       dependencies=[Depends(current_active_user)])

    @app.post("/gen_report/", dependencies=[Depends(current_active_user)])
    async def create_report(report: ReportFormat):
        """Generate Report contain users discount codes

        Trigger AWS Lambda and query AWS RDS MySQL and upload report to S3
        """
        # TODO: Trigger
        from yretain.app.aws.sns import publish_message
        from yretain.app.aws.sns import topic
        import boto3
        import json

        lambda_client = boto3.client('lambda', region_name="us-east-1")

        test_event = dict()
        # APi -> Lambda -> AWS RDS MySQl Report -> S3-> SNS -> EMAIL

        response = lambda_client.invoke(
          FunctionName='lam-new',
          Payload=json.dumps(test_event),
        )

        response_payload = response['Payload'].read().decode("utf-8")
        print(f"lambda response payload: {response_payload}")
        msg = f"{str(report)} {response_payload['s3']}"

        publish_message(topic, str(msg))

        return msg

    @app.post("/email_report/", dependencies=[Depends(current_active_user)])
    async def email_report(report: ReportFormat, use_aws_sns: bool = False):
        """Once the Report is generated call email report to send report is avilable to users:
        - Customer Retention team
        - Marketing team

        Trigger AWS SNS and send email to users
        """
        if use_aws_sns:
            from yretain.app.aws.sns import publish_message
            from yretain.app.aws.sns import topic
            publish_message(topic, str(report))
            return report
        else:
            # TODO: Implement email report
            pass


    @app.get("/authenticated-route")
    async def authenticated_route(user: User = Depends(current_active_user)):
        return {"message": f"Hello {user.email}!"}

    return app
