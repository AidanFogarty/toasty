import os

from aws_cdk import BundlingOptions, Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from constructs import Construct

from toastypy.constructs.lambda_warmer import LambdaWarmer


class ExamplesStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, environment: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_warmer_function = _lambda.Function(
            self,
            "LambdaWarmer",
            code=_lambda.Code.from_asset(
                os.path.join(os.getcwd(), "examples/example_function"),
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "pip install --index-url https://test.pypi.org/simple/ -r requirements.txt -t /asset-output && cp -au . /asset-output",
                    ],
                ),
            ),
            handler="example_function_handler.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            description="Lambda warmer function to be kept warm",
            log_retention=logs.RetentionDays.ONE_WEEK
            if environment != "prod"
            else logs.RetentionDays.TWO_YEARS,
            memory_size=512,
        )

        LambdaWarmer(
            self,
            "LambdaWarmerConstruct",
            concurrency=20,
            lambda_to_warm_arn=lambda_warmer_function.function_arn,
            environment=environment,
        )
