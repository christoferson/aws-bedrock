import os
import boto3
import demo_prompt

print(f"Python Version: {boto3.__version__}")

# Use AWS_PROFILE from environment variable
# boto3.Session() will automatically use credentials from the profile
session = boto3.Session()

demo_prompt.run_demo(session)


print("End")