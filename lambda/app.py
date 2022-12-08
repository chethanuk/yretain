import json
import requests
import sqlalchemy
import pymysql
import json
import boto3
import io
import numpy as np


from botocore.exceptions import ClientError

# To get list of buckets present in AWS using S3 client
s3 = boto3.client('s3')
AWS_S3_BUCKET="yathena"
def get_buckets_client():
    buckets = s3.buckets.all()
    return buckets

def handler(event, context):
    print(f"context: {context} and event: {event}")
    
    import pandas as pd 
    from sqlalchemy import create_engine
    my_conn = create_engine("mysql+pymysql://admin:wi8NTq7yQ8DQCz8@database-1.cujnaavuyxu8.us-east-1.rds.amazonaws.com:3306/yretain")
    
    query = """
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
            WHEN inactive_days < 3 THEN 'INSTANT_10_UPTO_100'
            WHEN inactive_days < 5 THEN 'INSTANT_20_UPTO_100'
            WHEN inactive_days < 8 THEN 'INSTANT_30_UPTO_100'
            WHEN inactive_days < 10 THEN 'INSTANT_40_UPTO_100'
        END AS DISCOUNTS
    FROM customer_inactive;
    """
    
    cus_discounts_df = pd.read_sql(query, my_conn)
    print(cus_discounts_df.head())
    
    full_s3_path = f"s3://{AWS_S3_BUCKET}/reports/customers/discounts_latest.csv"
    with io.StringIO() as csv_buffer:
        cus_discounts_df.to_csv(csv_buffer, index=False)
    
        response = s3.put_object(
            Bucket=AWS_S3_BUCKET, Key="reports/customers/discounts_latest.csv", 
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