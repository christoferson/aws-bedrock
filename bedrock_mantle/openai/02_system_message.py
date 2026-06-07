from openai import OpenAI
from aws_bedrock_token_generator import provide_token

OPENAI_BASE_URL="https://bedrock-mantle.us-east-2.api.aws/openai/v1"

client = OpenAI(
    api_key=provide_token(region="us-east-2"),
    base_url=OPENAI_BASE_URL,
    project="default",
)

response = client.responses.create(
    model="openai.gpt-5.5",
    input="Can you explain the features of Amazon Bedrock?",
    instructions="You are a helpful AI assistant with expertise in AWS services and cloud computing.",
)

print(response)