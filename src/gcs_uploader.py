# src/gcs_uploader.py
import os
from google.cloud import storage

def upload_file(bucket_name: str, source_file_path: str, dest_blob_name: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(dest_blob_name)
    blob.upload_from_filename(source_file_path)
    return True
