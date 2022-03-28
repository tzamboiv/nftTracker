import json
import requests
import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import os
import time
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit# import requests

db = boto3.client('dynamodb')

metrics = Metrics(namespace='nftTracker', service='transactionScrapper')

@metrics.log_metrics
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

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    block = event['Records'][0]['body']
    response = getBlock("0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d", os.environ['API_KEY'], block)
    #response = getBlock("0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d", '', block)

    print(response['status'])
    if (response['status'] == '1'):
        print('triggered')
        metrics.add_metric(name = 'SuccessFullPull', unit=MetricUnit.Count, value = 1)
    elif (response['status'] == '0') & (response['message'] == 'NOTOK') & (response['result'] == "Max rate limit reached"):

        metrics.add_metric(name = 'RateLimitExceeded', unit=MetricUnit.Count, value = 1)
        raise Exception('request failed')
    elif (response['status'] == '0') & (response['message'] == 'No transactions found') & (len(response['result']) == 0):
        metrics.add_metric(name = 'EmptyBlock', unit=MetricUnit.Count, value = 1)
    else:
        metrics.add_metric(name = 'UnknownReturn', unit=MetricUnit.Count, value = 1)
        print(response['message'])
        print(response['result'])

    results = response['result']
    item = {}
    item['blockNumber'] = {'S': block}
    db.put_item(TableName='blockNumberCheck', Item = item)
    resultsFormattedForDynamoDB = [formatJsontoDynamodb(i) for i in results]
    #print(resultsFormattedForDynamoDB)
    for i in resultsFormattedForDynamoDB:
        db.put_item(TableName='baycData', Item = i)
    time.sleep(1)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }

def getBlock(contract_address, apiKey, block, sort = 'desc'):
    queryURL = 'module=account&action=tokennfttx&contractaddress=' + contract_address + '&sort=' + sort + '&page=1&offset=10000'
     #q = etherscan.accounts.get_erc721_token_transfer_events_by_contract_address_paginated(contract_address = contract_address, page = 1, offset = 10000, sort = sort)
    #print(queryURL)
    requestURL = "https://api.etherscan.io/api?" + queryURL + "&endblock=" + str(block) + '&startblock=' + str(block) + '&apikey=' + str(apiKey)
    #print(requestURL)
    response = requests.get(requestURL)

    jsonResponse = json.loads(response.text)
    print(jsonResponse['status'])

    #if (jsonResponse['status'] != '1') & (jsonResponse['message'] == 'NOTOK'):
        #print(jsonResponse['result'])
    #    print(jsonResponse['message'])
    #    raise Exception('request failed')
    return jsonResponse

def formatJsontoDynamodb(pythonDict):
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in pythonDict.items()
    }
