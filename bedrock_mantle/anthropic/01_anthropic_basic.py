import logging
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle()

response = client.messages.create(
    #model="anthropic.claude-opus-4-7",
    model="anthropic.claude-haiku-4-5",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hi There"}]
)

text_response = response.content[0].text
print(f"Response: {text_response}")
