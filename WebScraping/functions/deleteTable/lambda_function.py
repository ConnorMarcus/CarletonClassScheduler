import boto3

TABLE_NAME = "carleton-courses"

def lambda_handler(event: dict, context: dict) -> str:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    
    # Delete the db and wait until its completed
    table.delete()
    table.wait_until_not_exists()
    
    return f"Table {TABLE_NAME} successfully deleted from DynamoDB!"