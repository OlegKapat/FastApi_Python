from collections.abc import Sequence
from contextlib import asynccontextmanager
from uuid import UUID

import aioboto3
from fastapi import UploadFile
from settings import settings


class S3Storage:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.session = aioboto3.Session()

    @asynccontextmanager
    async def get_s3_client(self):
        async with self.session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION_NAME,
        ) as s3_client:
            yield s3_client

    async def upload_file_to_s3(
        self,
        files: UploadFile | list[UploadFile],
        uuid_obj: UUID | str,
        root_dir: str = "productImages",
        return_first: bool = False,
    ):
        # Normalize to list in a runtime-safe way
        if not isinstance(files, Sequence) or isinstance(files, (str, bytes)):
            files = [files]
        urls = []
        async with self.get_s3_client() as s3_client:
            for file in files:
                await file.seek(0)
                object_name = f"{root_dir}/{str(uuid_obj)}/{file.filename}"
                await s3_client.upload_fileobj(file.file, self.bucket_name, object_name)
                urls.append(f"{settings.S3_PUBLIC_URL}/{object_name}")

            if return_first:
                return urls[0] if urls else None

        return urls


s3_storage = S3Storage()
