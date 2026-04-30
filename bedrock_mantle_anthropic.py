import logging
import os
from anthropic import AnthropicBedrockMantle

#logging.basicConfig(level=logging.DEBUG)
#print(os.environ.get("AWS_PROFILE"))
#print(os.environ.get("AWS_REGION"))

client = AnthropicBedrockMantle()

response = client.messages.create(
    model="anthropic.claude-opus-4-7",
    max_tokens=256,
    messages=[{"role": "user", "content": "What is the capital of France?"}]
)

text_response = response.content[0].text
print(f"Response: {text_response}")
