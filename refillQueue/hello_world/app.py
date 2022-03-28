import json
import boto3
import os

sqs = boto3.client('sqs')




def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    print(event['Records'])
    print(os.environ["ORIGINAL_QUEUE"])
    response = populateSQS(event['Records'], os.environ["ORIGINAL_QUEUE"])
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
def populateSQS(messageList, queueUrl):
    res=[]
    for i in messageList:
        res.append(sqs.send_message(
        QueueUrl = queueUrl,
        MessageBody = str(i['body'])
        ))
    return res
