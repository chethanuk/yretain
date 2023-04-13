Create a new IAM role that allows Lambda to interact with other AWS services. You can use the following command to create a new IAM role named lambda-docker-role:

aws iam create-role --role-name lambda-docker-role --assume-role-policy-document '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
Attach a policy to the IAM role that grants access to the ECR repository where the Docker image is stored. You can use the following command to attach the AmazonEC2ContainerRegistryPowerUser policy to the lambda-docker-role role:


aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser --role-name lambda-docker-role
Build the Docker image and push it to your ECR repository. Make sure to replace REPOSITORY_URI with the URI of your ECR repository and IMAGE_TAG with the tag you want to use for the image.

docker build -t REPOSITORY_URI:IMAGE_TAG .
docker push REPOSITORY_URI:IMAGE_TAG
Create a new Lambda function with the docker runtime and the IAM role you created earlier. You can use the following command to create a new Lambda function named my-lambda-function:

aws lambda create-function --function-name my-lambda-function --role lambda-docker-role --code ImageUri=REPOSITORY_URI:IMAGE_TAG --package-type Image --memory-size 1024 --timeout 60 --runtime docker
This command specifies the image URI, memory size, timeout, and runtime for the Lambda function.

Test the Lambda function by invoking it with a test event. You can use the following command to invoke the Lambda function:

by running invoke
