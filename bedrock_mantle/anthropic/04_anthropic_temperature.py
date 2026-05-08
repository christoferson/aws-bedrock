import logging
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle()


system = """
You are a helpful assistant that generates movie ideas. You are creative and imaginative, and you always come up with unique and interesting ideas. You are also concise, and you always generate one sentence movie ideas.
"""

messages = [
    {"role": "user", "content": "Generate a one sentence movie idea"},
]

print(f"\n\nLow temperature\n\n")

# Low temperature
response = client.messages.create(
    model="anthropic.claude-opus-4-7",
    max_tokens=256,
    system=system,
    #temperature=0.2, #{'type': 'invalid_request_error', 'message': '`temperature` is deprecated for this model.'}}
    messages=messages
)

text_response = response.content[0].text
print(f"Response: {text_response}")

print(f"\n\nHigh temperature\n\n")

# High temperature
response = client.messages.create(
    model="anthropic.claude-opus-4-7",
    max_tokens=256,
    system=system,
    #temperature=1.0,
    messages=messages
)

text_response = response.content[0].text
print(f"Response: {text_response}")
