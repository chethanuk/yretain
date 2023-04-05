# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError

# def create_topic(name):
#     """
#     Creates a notification topic.
#
#     :param name: The name of the topic to create.
#     :return: The newly created topic.
#     """
#     sns = boto3.resource("sns")
#     topic = sns.create_topic(Name=name)
#     return topic
#
# print(create_topic("customer-discounts"))
# arn:aws:sns:us-east-1:470594810414:learnaws-boto3-sns




def get_secret(secret_name="prod/mysql", region_name="us-east-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    # Your code goes here.
    return secret

print(get_secret("rds-db-credentials"))