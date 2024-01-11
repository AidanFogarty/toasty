import aws_cdk as cdk
from constructs import Construct
from aws_cdk.assertions import Template
import pytest

from src.toastypy.constructs.lambda_warmer import LambdaWarmer


class LambdaWarmerTestStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        LambdaWarmer(
            self,
            "LambdaWarmer",
            concurrency=1,
            lambda_to_warm_arn="arn:aws:lambda:us-east-1:123456789012:function:my-lambda",
            environment="dev",
        )


@pytest.fixture
def lambda_warmer_test_stack():
    app = cdk.App()

    test_lambda_warmer_stack = LambdaWarmerTestStack(
        app,
        "TestLambdaWarmerStack",
        stack_name="TestLambdaWarmerStack",
        description="Test Lambda Warmer Stack",
        env=cdk.Environment(account="123456789", region="us-east-1"),
    )

    return Template.from_stack(test_lambda_warmer_stack)


def test_app_contains_lambda_warmer_function(lambda_warmer_test_stack):
    lambda_warmer_test_stack.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Environment": {
                "Variables": {
                    "ENVIRONMENT": "dev",
                    "CONCURRENCY": "1",
                    "TARGET_ARN": "arn:aws:lambda:us-east-1:123456789012:function:my-lambda",
                }
            },
            "Runtime": "python3.11",
        },
    )


def test_lambda_warmer_can_invoke_function(lambda_warmer_test_stack):
    lambda_warmer_test_stack.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Statement": [
                    {
                        "Action": "lambda:InvokeFunction",
                        "Effect": "Allow",
                        "Resource": "arn:aws:lambda:us-east-1:123456789012:function:my-lambda",
                    }
                ],
                "Version": "2012-10-17",
            },
        },
    )
