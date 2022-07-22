from __future__ import annotations
import logging
import random
import string
import typing as t
import uuid

import boto3
import boto3.session
import fastapi

s3: None | t.Any = None

logger = logging.getLogger(__name__)

BUCKET_NAME = 'nux'
ENDPOINT_URL = 'https://storage.yandexcloud.net'


class S3NotInitializedError(Exception):
    pass


def setup_s3(aws_access_key_id, aws_secret_access_key):
    global s3, s3_session

    print(aws_access_key_id, aws_secret_access_key)
    s3_session = boto3.session.Session(
    )
    s3 = s3_session.client(
        service_name='s3',
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='ru-central1',
    )


def print_shit():
    if s3 is None:
        raise S3NotInitializedError

    for key in s3.list_objects(Bucket=BUCKET_NAME)['Contents']:
        print(key['Key'])


def generate_random_string():
    return ''.join(random.choices(string.ascii_letters, k=10))


def upload_file(file, filename):
    if s3 is None:
        raise S3NotInitializedError

    s3.upload_fileobj(file, BUCKET_NAME, filename)
    return f"{ENDPOINT_URL}/{BUCKET_NAME}/{filename}"


def determine_type(mime_type):
    d = {
        "image/jpeg": "jpg",
        "image/png": "png",
    }
    return d[mime_type]


def upload_fastapi_file(file: fastapi.UploadFile, *path):
    path = [s or generate_random_string() for s in path]
    filename = '/'.join(path)
    full_filename = filename + '.' + determine_type(file.content_type)
    return upload_file(file.file, full_filename)
