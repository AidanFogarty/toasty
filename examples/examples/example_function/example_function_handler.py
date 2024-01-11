from toastypy.toastypy import toasty


@toasty
def lambda_handler(event, context):
    print("Hello World!")
    return {"statusCode": 200, "body": "Success"}
