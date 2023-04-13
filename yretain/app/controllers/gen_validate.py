import io
import pandas as pd
import boto3
import sqlalchemy
from sqlalchemy.pool import QueuePool

# To get list of buckets present in AWS using S3 client
s3 = boto3.client('s3')
AWS_S3_BUCKET = "yathena"

# RDS database configuration
DB_USER = "admin"
DB_PASSWORD = "wi8NTq7yQ8DQCz8"
DB_NAME = "yretain"
DB_HOST = "database-1.cujnaavuyxu8.us-east-1.rds.amazonaws.com"
DB_PORT = 3306

# SQLAlchemy connection engine
db_engine = sqlalchemy.create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    poolclass=QueuePool,
    pool_recycle=3600,
    pool_size=10
)


def gen_report(is_holdiay=False):
    if is_holdiay:
        HOLIDAY_3 = "INSTANT_10_UPTO_100"
        HOLIDAY_5 = "INSTANT_20_UPTO_100"
        HOLIDAY_8 = "INSTANT_30_UPTO_100"
        HOLIDAY_10 = "INSTANT_40_UPTO_100"
    else:
        HOLIDAY_3 = "INSTANT_15_UPTO_100"
        HOLIDAY_5 = "INSTANT_25_UPTO_100"
        HOLIDAY_8 = "INSTANT_35_UPTO_100"
        HOLIDAY_10 = "INSTANT_45_UPTO_100"

    query = f"""
    WITH last_activity AS (
        select phone_number,
            MAX(updated) AS last_order_time,
            CURRENT_TIMESTAMP as now
        from yretain.customers_activity
        GROUP BY phone_number
    ),
    customer_inactive AS (
        SELECT *,
               datediff(now, last_order_time) as inactive_days
        FROM last_activity
    )
    SELECT *,
        CASE
            WHEN inactive_days < 3 THEN '{HOLIDAY_3}'
            WHEN inactive_days < 5 THEN '{HOLIDAY_5}'
            WHEN inactive_days < 8 THEN '{HOLIDAY_8}'
            WHEN inactive_days < 10 THEN '{HOLIDAY_10}'
        END AS DISCOUNTS
    FROM customer_inactive;
    """

    cus_discounts_df = pd.read_sql(query, db_engine)
    print(cus_discounts_df.head())

    full_s3_path = f"s3://{AWS_S3_BUCKET}/reports/customers/discounts_latest.csv"
    with io.StringIO() as csv_buffer:
        cus_discounts_df.to_csv(csv_buffer, index=False)

        response = s3.put_object(
            Bucket=AWS_S3_BUCKET,
            Key="reports/customers/discounts_latest.csv",
            Body=csv_buffer.getvalue()
        )

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status == 200:
            print(f"Successful S3 put_object response. Status - {status}")
        else:
            print(f"Unsuccessful S3 put_object response. Status - {status}")

    return {
        'statusCode': 200,
        'body': str(cus_discounts_df.head()),
        's3': full_s3_path
    }
