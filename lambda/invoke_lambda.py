import boto3, json

lambda_client = boto3.client('lambda')

test_event = dict()

response = lambda_client.invoke(
  FunctionName='lam-new',
  Payload=json.dumps(test_event),
)

print(response['Payload'].read().decode("utf-8"))