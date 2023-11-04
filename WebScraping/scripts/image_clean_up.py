import os
import boto3

repository_name = os.environ.get("REPO_NAME")

def delete_all_ecr_images(repository_name):
    ecr = boto3.client("ecr")

    # List the images in the repository
    images = ecr.list_images(repositoryName=repository_name).get("imageIds", [])

    if not images:
        print("No images found in the repository.")
        return

    # Batch delete the images
    ecr.batch_delete_image(repositoryName=repository_name, imageIds=images)
    
    print("Deleted all image(s)")

if __name__ == "__main__":
    delete_all_ecr_images(repository_name)
