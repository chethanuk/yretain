import boto3

sns = boto3.resource("sns", region_name="us-east-1")


def create_topic(name):
    """
    Creates a notification topic.

    :param name: The name of the topic to create.
    :return: The newly created topic.
    """
    topic = sns.create_topic(Name=name)
    return topic


def publish_message(topic, message):
    """
    Publishes a message to a SNS topic.

    :param topic: The topic to publish to.
    :param message: The message to publish.
    :return: The ID of the message.
    """
    response = topic.publish(Message=message)
    message_id = response['MessageId']
    return message_id


# topic = create_topic("customer-discounts")
topic = sns.Topic(arn="arn:aws:sns:us-east-1:470594810414:customer-discounts")

