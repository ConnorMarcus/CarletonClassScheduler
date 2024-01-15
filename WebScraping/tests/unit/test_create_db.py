from unittest.mock import patch, MagicMock
from WebScraping.functions.createTable.lambda_function import *

def test_lambda_handler():
    with patch("boto3.resource") as mock_resource:
        expected_table_name = "carleton-courses"
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_resource.return_value = mock_dynamodb
        mock_dynamodb.create_table.return_value = mock_table
        
        # Running the actual lambda handler
        result = lambda_handler(event={}, context={})

        mock_resource.assert_called_with("dynamodb")
        mock_dynamodb.create_table.assert_called_with(
            TableName=expected_table_name,
            KeySchema=[
                {'AttributeName': 'Subject', 'KeyType': 'HASH'},
                {'AttributeName': 'Term', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'Subject', 'AttributeType': 'S'},
                {'AttributeName': 'Term', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
        )
        mock_table.wait_until_exists.assert_called_once()
        assert result == f"Table {expected_table_name} successfully created!"
