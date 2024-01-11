# 🍞 Toasty - The Lambda Warmer

Toasty is a simple Python library designed to keep your AWS Lambda functions warm using an EventBridge schedule. It provides a decorator `@toasty` for your Lambda functions and a CDK construct `LambdaWarmer` for setting up the warming schedule.

## Installation

You can install the Toasty library using pip:

```bash
pip install toastypy
```

## Usage

### Toasty Wrapper

The `@toasty` wrapper can be used to decorate your Lambda functions. Here's an example:

```py
from toastypy.toastypy import toasty

@toasty
def my_lambda_function(event, context):
    # Your function logic here
    pass
```

### LambdaWarmer CDK Constuct

The `LambdaWarmer` construct can be used in your CDK stack to set up the warming schedule for your Lambda functions. Here's an example:

```py
from aws_cdk import aws_lambda as _lambda
from toastypy.constructs.lambda_warmer import LambdaWarmer

# Assuming `app` and `stack_id` are your CDK app and stack ID
my_lambda = _lambda.Function(
    app, "MyLambdaFunction",
    # Lambda function properties here
)

LambdaWarmer(
    app, "MyLambdaWarmer",
    lambda_to_warm_arn=my_lambda.function_arn,
    concurrency=20,
    environment="nonprod",
)
```

In this example, LambdaWarmer is set up to warm my_lambda function. The concurrency parameter specifies how many concurrent executions to use for warming, and environment is an optional parameter for specifying the environment.

Please refer to the LambdaWarmer and toasty in the source code for more details.