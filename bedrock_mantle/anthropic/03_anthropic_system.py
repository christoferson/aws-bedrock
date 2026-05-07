import logging
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle()


system = """
You are a patient mathematics tutor who helps students understand mathematical concepts and solve problems.
Do not directly solve the problem for the student, but instead guide them through the process of finding the solution on their own.
You provide clear explanations, step-by-step solutions, and encourage critical thinking. 
You are friendly, supportive, and always aim to make learning enjoyable for your students.
"""

messages = [
    {"role": "user", "content": "How do I solve 5x+3=2 for x?"},
]

printf("\n\nNo system message\n\n")

# No system message
response = client.messages.create(
    model="anthropic.claude-opus-4-7",
    max_tokens=256,
    messages=messages
)

text_response = response.content[0].text
print(f"Response: {text_response}")

printf("\n\nNow with system message\n\n")

# With system message
response = client.messages.create(
    model="anthropic.claude-opus-4-7",
    max_tokens=256,
    system=system,
    messages=messages
)

text_response = response.content[0].text
print(f"Response: {text_response}")
