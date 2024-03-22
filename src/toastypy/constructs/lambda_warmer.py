from aws_cdk import Duration
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
import aws_cdk.aws_scheduler_alpha as scheduler
import aws_cdk.aws_scheduler_targets_alpha as scheduler_targets
from constructs import Construct


class LambdaWarmer(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        concurrency: int,
        lambda_to_warm_arn: str,
        environment: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.lambda_warmer_function = _lambda.Function(
            self,
            "LambdaWarmer",
            code=_lambda.Code.from_inline(
                """
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

    return {"statusCode": 200, "body": "Lambda warmer function is warming up a lambda"}"""
            ),
            handler="index.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            description="Lambda warmer function to keep a lambda warm",
            log_retention=(
                logs.RetentionDays.ONE_WEEK
                if environment != "prod"
                else logs.RetentionDays.TWO_YEARS
            ),
            timeout=Duration.seconds(30),
            environment={
                "ENVIRONMENT": environment,
                "CONCURRENCY": str(concurrency),
                "TARGET_ARN": lambda_to_warm_arn,
            },
        )

        self.lambda_warmer_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[lambda_to_warm_arn],
            )
        )

        lambda_warmer_schedule_role = iam.Role(
            self,
            "LambdaWarmerScheduleRole",
            assumed_by=iam.ServicePrincipal("scheduler.amazonaws.com"),
            description="Role for the lambda warmer schedule to invoke the lambda warmer function",
            inline_policies={
                "lambda_warmer_schedule_policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["lambda:InvokeFunction"],
                            resources=[self.lambda_warmer_function.function_arn],
                        )
                    ]
                ),
            },
        )

        lambda_warmer_target = scheduler_targets.LambdaInvoke(
            self.lambda_warmer_function,
            role=lambda_warmer_schedule_role,
        )

        scheduler.Schedule(
            self,
            "LambdaWarmerScheduler",
            schedule=scheduler.ScheduleExpression.rate(Duration.minutes(5)),
            target=lambda_warmer_target,
            description=f"Lambda warmer schedule to keep {lambda_to_warm_arn} warm",
        )
