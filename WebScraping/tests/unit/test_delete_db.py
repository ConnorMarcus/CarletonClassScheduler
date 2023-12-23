from WebScraping.functions.deleteTable.lambda_function import *
from unittest.mock import patch

def test_lambda_handler():
    with patch("boto3.resource") as mock_dynamodb:
        mock_table = mock_dynamodb().Table.return_value

        with patch.object(mock_table, 'delete') as mock_delete, \
            patch.object(mock_table, 'wait_until_not_exists') as mock_wait:

            result = lambda_handler(event={}, context={})

            mock_delete.assert_called_once()
            mock_wait.assert_called_once()
            assert result == "Table carleton-courses successfully deleted from DynamoDB!"
