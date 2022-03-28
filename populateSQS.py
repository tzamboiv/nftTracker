import boto3

def populateSQS(startBlock, endBlock, queueUrl):
    sqs = boto3.client('sqs')
    for i in range(startBlock, endBlock + 1):
        print(i)
        sqs.send_message(
        QueueUrl = queueUrl,
        MessageBody = str(i)
        )
    return
