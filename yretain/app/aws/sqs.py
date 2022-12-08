import json

import boto3

sns = boto3.resource("sns", region_name="us-east-1")

sqs = boto3.client("sqs", region_name="us-east-1")


def create_queue(name="customer-discounts-queue"):
    response = sqs.create_queue(
        QueueName="customer-discounts-queue",
        Attributes={
            "DelaySeconds": "0",
            "VisibilityTimeout": "60",  # 60 seconds
        }
    )
    print(response)


def get_queue_url(name="customer-discounts-queue"):
    response = sqs.get_queue_url(
        QueueName=name,
    )
    return response["QueueUrl"]


def send_message(coupon, coupon_msg, coupon_expiry, phone_num, email, name="customer-discounts-queue"):
    message = {
        'coupon': coupon,
        'message': coupon_msg,
        'expiry': coupon_expiry,
        'phone_num': phone_num,
        'email': email,
    }
    response = sqs.send_message(
        QueueUrl=get_queue_url(name),
        MessageBody=json.dumps(message)
    )
    print(response)


create_queue()
get_queue_url()
