from __future__ import annotations
import logging
import random
import string
import typing as t
import uuid
import re

import boto3
import boto3.session
import fastapi

s3: None | t.Any = None
bucket: None | t.Any = None
resource: None | t.Any = None

logger = logging.getLogger(__name__)

BUCKET_NAME = 'nux'
ENDPOINT_URL = 'https://storage.yandexcloud.net'


class S3NotInitializedError(Exception):
    pass


def setup_s3(aws_access_key_id, aws_secret_access_key):
    global s3, s3_session, bucket, resource

    s3_session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='ru-central1',
    )
    r: t.Any = s3_session.resource(
        's3',
        endpoint_url=ENDPOINT_URL,
    )
    resource = r
    assert resource is not None
    bucket = resource.Bucket(BUCKET_NAME)
    s3 = s3_session.client(
        service_name='s3',
        endpoint_url=ENDPOINT_URL,
    )
    assert s3 is not None


def _get_url(filename):
    return f"{ENDPOINT_URL}/{BUCKET_NAME}/{filename}"


def list_objects(*path, patern=r".*\..*") -> list[str]:
    if bucket is None:
        raise S3NotInitializedError

    path = '/'.join(path) + '/'

    keys = (o.key for o in bucket.objects.filter(Prefix=path))
    keys = (key for key in keys if re.fullmatch(patern, key))
    keys = (_get_url(key) for key in keys)
    keys = list(keys)
    return keys


def generate_random_string():
    return ''.join(random.choices(string.ascii_letters, k=10))


def upload_file(file, filename):
    if s3 is None:
        raise S3NotInitializedError

    s3.upload_fileobj(file, BUCKET_NAME, filename)
    return _get_url(filename)


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
