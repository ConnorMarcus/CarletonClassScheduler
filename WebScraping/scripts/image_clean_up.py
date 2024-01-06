import os
import boto3

def delete_all_ecr_images(repository_name: str) -> None:
    # Make sure REPO_NAME env var is found
    if repository_name == "":
        print("Missing Repository Env Variable!")
        return
    
    ecr = boto3.client("ecr")

    # List the images in the repository
    images = ecr.list_images(repositoryName=repository_name).get("imageIds", [])

    if not images:
        print("No images found in the repository.")
        return

    # Batch delete the images
    ecr.batch_delete_image(repositoryName=repository_name, imageIds=images)
    
    print("Deleted all image(s)")

# Run the script
repository_name = os.environ.get("REPO_NAME", "")
delete_all_ecr_images(repository_name)
