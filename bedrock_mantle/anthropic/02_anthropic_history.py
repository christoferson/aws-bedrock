import logging
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle()

messages = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "How many people live there?"}
]

response = client.messages.create(
    model="anthropic.claude-opus-4-7",
    max_tokens=256,
    messages=messages
)

text_response = response.content[0].text
print(f"Response: {text_response}")
