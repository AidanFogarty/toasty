import asyncio
import os
import json
import uuid
import logging

import boto3

logger = logging.getLogger(__name__)
client = boto3.client("lambda")

TARGET_ARN = os.environ["TARGET_ARN"]
CONCURRENCY = int(os.environ["CONCURRENCY"])


def lambda_handler(event, context):
    logger.info(
        {"message": "lambda warmer triggering target lambda", "target_arn": TARGET_ARN}
    )

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(warm_lambda_functions())


async def invoke_lambda(index: int):
    toasty_id = f"toasty-{uuid.uuid4()}"
    payload = {
        "type": "toasty",
        "toasty_id": toasty_id,
        "concurrency": CONCURRENCY,
        "concurrency_index": index,
    }

    client.invoke(
        FunctionName=TARGET_ARN,
        InvocationType="Event",
        Payload=json.dumps(payload),
    )


async def warm_lambda_functions():
    invokers = [invoke_lambda(index) for index in range(CONCURRENCY)]
    await asyncio.gather(*invokers)

    return {"statusCode": 200, "body": "Lambda warmer function is warming up a lambda"}
