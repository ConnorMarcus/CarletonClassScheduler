import boto3

TABLE_NAME = "carleton-courses"

def lambda_handler(event: dict, context: dict) -> str:
    '''
    Creates an Amazon DynamoDB table that is used to store carleton course
    information.

    Parameters:
    event: event that triggers the Lambda function.
    context: the Lambda function execution context.

    Returns: 
    - str: A message indicating that the DynamoDB table has been successfully created. 
    '''
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.create_table(TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'Subject', 
                    'KeyType': 'HASH' # Partition Key
                },
                {
                    'AttributeName': 'Term',
                    'KeyType': 'RANGE' # Sort Key 
                }
            ], 
            AttributeDefinitions=[
                {
                    'AttributeName': 'Subject',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Term',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
    )

    # Wait until Database is created before returning
    table.wait_until_exists()
    
    return f"Table {TABLE_NAME} successfully created!"
