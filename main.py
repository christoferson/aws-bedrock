import os
import boto3
import config
import demo_prompt

print(f"Python Version: {boto3.__version__}")

session = boto3.Session(
    aws_access_key_id=config.aws["aws_access_key_id"],
    aws_secret_access_key=config.aws["aws_secret_access_key"],
    region_name=config.aws["region_name"],
)

demo_prompt.run_demo(session)


print("End")