import time
from dataclasses import dataclass
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from copypaste.config import Config
from copypaste.ids import generate_id

MAX_PASTE_SIZE_BYTES = 380 * 1024
MAX_ID_ALLOCATION_ATTEMPTS = 5


class PasteTooLargeError(Exception):
    pass


@dataclass(frozen=True)
class Paste:
    content: str
    title: str | None = None


def get_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=Config.DYNAMODB_ENDPOINT_URL,
        region_name=Config.AWS_REGION,
    )


def _ensure_ttl_enabled(resource, table_name):
    try:
        resource.meta.client.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={"Enabled": True, "AttributeName": "expires_at"},
        )
    except ClientError as error:
        if error.response["Error"]["Code"] != "ValidationException":
            raise


def create_table(resource, table_name=None):
    table_name = table_name or Config.PASTE_TABLE_NAME
    if table_name in (t.name for t in resource.tables.all()):
        table = resource.Table(table_name)
    else:
        table = resource.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "paste_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "paste_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()

    _ensure_ttl_enabled(resource, table_name)
    return table


def put_paste(
    table, content: str, title: str | None = None, expires_in_seconds: int | None = None
) -> str:
    content_bytes = len(content.encode("utf-8"))
    if content_bytes > MAX_PASTE_SIZE_BYTES:
        raise PasteTooLargeError(
            f"paste content is {content_bytes} bytes, exceeds the {MAX_PASTE_SIZE_BYTES}-byte limit"
        )

    created_at = datetime.now(timezone.utc).isoformat()

    item = {"content": content, "created_at": created_at}
    if title:
        item["title"] = title
    if expires_in_seconds is not None:
        item["expires_at"] = int(time.time()) + expires_in_seconds

    for _ in range(MAX_ID_ALLOCATION_ATTEMPTS):
        paste_id = generate_id()
        try:
            table.put_item(
                Item={"paste_id": paste_id, **item},
                ConditionExpression="attribute_not_exists(paste_id)",
            )
            return paste_id
        except ClientError as error:
            if error.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise

    raise RuntimeError("failed to allocate a unique paste id after retries")


def get_paste(table, paste_id: str) -> Paste | None:
    response = table.get_item(Key={"paste_id": paste_id})
    item = response.get("Item")
    if not item:
        return None
    if "expires_at" in item and item["expires_at"] <= int(time.time()):
        return None
    return Paste(content=item["content"], title=item.get("title"))
