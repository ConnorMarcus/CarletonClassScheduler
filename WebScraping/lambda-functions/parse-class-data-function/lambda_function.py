import json
from bs4 import BeautifulSoup

def handler(event, context):

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda')
    }
