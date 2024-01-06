from WebScraping.scripts.image_clean_up import *
from unittest.mock import Mock, patch

TEST_REPO_NAME = "TestRepo"

def test_delete_all_ecr_images():
  with patch("boto3.client") as mock_client:
    mock_ecr = Mock()
    mock_client.return_value = mock_ecr

    mock_ecr.list_images.return_value = {"imageIds": ["image_id_1", "image_id_2"]}
    mock_ecr.batch_delete_image.return_value = {"imageIds": ["image_id_1", "image_id_2"]}

    delete_all_ecr_images(TEST_REPO_NAME)

    mock_ecr.list_images.assert_called_once_with(repositoryName=TEST_REPO_NAME)
    mock_ecr.batch_delete_image.assert_called_once_with(repositoryName=TEST_REPO_NAME, imageIds=["image_id_1", "image_id_2"])


def test_delete_all_ecr_images_no_images():
  with patch("boto3.client") as mock_client:
    mock_ecr = Mock()
    mock_client.return_value = mock_ecr

    mock_ecr.list_images.return_value = {"imageIds": []}

    delete_all_ecr_images(TEST_REPO_NAME)

    mock_ecr.list_images.assert_called_once_with(repositoryName=TEST_REPO_NAME)
    mock_ecr.batch_delete_image.assert_not_called()
