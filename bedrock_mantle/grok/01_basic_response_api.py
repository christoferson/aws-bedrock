from openai import OpenAI
from aws_bedrock_token_generator import provide_token

OPENAI_REGION = "us-west-2"
OPENAI_BASE_URL=f"https://bedrock-mantle.{OPENAI_REGION}.api.aws/openai/v1"

client = OpenAI(
    api_key=provide_token(region=OPENAI_REGION),
    base_url=OPENAI_BASE_URL,
    project="default",
)

response = client.responses.create(
    model="xai.grok-4.3",
    input="Can you explain the features of Amazon Bedrock?"
)
print(response)