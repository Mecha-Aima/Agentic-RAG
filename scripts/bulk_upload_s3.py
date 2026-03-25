# scripts/bulk_upload_s3.py
import boto3
import os
import sys
import threading
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError

def ensure_bucket_exists(bucket_name: str, region: str | None = None):
    """
    Create the S3 bucket if it doesn't exist (in this account).
    No-op if the bucket already exists and you have access.
    """
    s3 = boto3.client("s3", region_name=region)

    try:
        s3.head_bucket(Bucket=bucket_name)
        return
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code not in ("404", "NoSuchBucket", "403", "AccessDenied"):
            raise

    params = {"Bucket": bucket_name}
    if region and region != "us-east-1":
        params["CreateBucketConfiguration"] = {"LocationConstraint": region}

    s3.create_bucket(**params)


def upload_directory(dir_path, bucket_name):
    """
    High-performance S3 uploader.
    """
    s3 = boto3.client('s3')

    region = os.getenv("AWS_REGION")
    ensure_bucket_exists(bucket_name, region=region)
    
    # Configure multipart upload
    config = TransferConfig(
        multipart_threshold=1024 * 25, # 25MB
        max_concurrency=20, # 20 threads
        multipart_chunksize=1024 * 25,
        use_threads=True
    )

    files_to_upload = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            local_path = os.path.join(root, file)
            # Maintain folder structure in S3
            s3_path = os.path.relpath(local_path, dir_path)
            files_to_upload.append((local_path, s3_path))

    print(f"Found {len(files_to_upload)} files. Starting upload...")

    def upload_file(args):
        local, remote = args
        try:
            print(f"Uploading {remote}...")
            s3.upload_file(local, bucket_name, remote, Config=config)
        except Exception as e:
            print(f"Failed to upload {remote}: {e}")

    # Use ThreadPool to blast files
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(upload_file, files_to_upload)

    print("✅ Bulk upload finished.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python bulk_upload_s3.py <local_dir> <bucket_name>")
        sys.exit(1)
    
    upload_directory(sys.argv[1], sys.argv[2])