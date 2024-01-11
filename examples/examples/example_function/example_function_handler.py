from toastypy.toastypy import toasty


@toasty
def lambda_handler(event, context):
    return {"statusCode": 200, "body": "Success"}
