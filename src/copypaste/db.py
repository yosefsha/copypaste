from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from copypaste.config import Config
from copypaste.ids import generate_id

MAX_PASTE_SIZE_BYTES = 380 * 1024
MAX_ID_ALLOCATION_ATTEMPTS = 5


class PasteTooLargeError(Exception):
    pass


def get_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=Config.DYNAMODB_ENDPOINT_URL,
        region_name=Config.AWS_REGION,
    )


def create_table(resource, table_name=None):
    table_name = table_name or Config.PASTE_TABLE_NAME
    if table_name in (t.name for t in resource.tables.all()):
        return resource.Table(table_name)

    table = resource.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "paste_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "paste_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table


def put_paste(table, content: str) -> str:
    content_bytes = len(content.encode("utf-8"))
    if content_bytes > MAX_PASTE_SIZE_BYTES:
        raise PasteTooLargeError(
            f"paste content is {content_bytes} bytes, exceeds the {MAX_PASTE_SIZE_BYTES}-byte limit"
        )

    created_at = datetime.now(timezone.utc).isoformat()

    for _ in range(MAX_ID_ALLOCATION_ATTEMPTS):
        paste_id = generate_id()
        try:
            table.put_item(
                Item={"paste_id": paste_id, "content": content, "created_at": created_at},
                ConditionExpression="attribute_not_exists(paste_id)",
            )
            return paste_id
        except ClientError as error:
            if error.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise

    raise RuntimeError("failed to allocate a unique paste id after retries")


def get_paste(table, paste_id: str) -> str | None:
    response = table.get_item(Key={"paste_id": paste_id})
    item = response.get("Item")
    return item["content"] if item else None
