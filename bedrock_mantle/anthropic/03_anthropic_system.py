import logging
from anthropic import AnthropicBedrockMantle
from service.constants.model import MODEL_DEFAULT_ID

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

def print_separator(char="=", length=80):
    print(char * length)

def print_section_header(title):
    print_separator()
    print(f"  {title}")
    print_separator()

def print_response(response, label):
    text_response = response.content[0].text
    token_usage = response.usage

    print(f"\n{label}:")
    print_separator("-")
    print(text_response)
    print_separator("-")
    print(f"Tokens - Input: {token_usage.input_tokens} | Output: {token_usage.output_tokens} | Total: {token_usage.input_tokens + token_usage.output_tokens}")
    print()

# Header
print("\n")
print_separator("=")
print("  ANTHROPIC CLAUDE - SYSTEM MESSAGE COMPARISON")
print_separator("=")

print(f"\nUser Question: {messages[0]['content']}")
print(f"Model: {MODEL_DEFAULT_ID}")
print(f"Max Tokens: 256\n")

# Test 1: No system message
print_section_header("TEST 1: WITHOUT SYSTEM MESSAGE")
response_no_system = client.messages.create(
    model=MODEL_DEFAULT_ID,
    max_tokens=256,
    messages=messages
)
print_response(response_no_system, "Response")

# Test 2: With system message
print_section_header("TEST 2: WITH SYSTEM MESSAGE")
print(f"\nSystem Prompt:\n{system}\n")
response_with_system = client.messages.create(
    model=MODEL_DEFAULT_ID,
    max_tokens=256,
    system=system,
    messages=messages
)
print_response(response_with_system, "Response")

# Summary comparison
print_section_header("COMPARISON SUMMARY")
print(f"{'Metric':<30} {'Without System':<20} {'With System':<20}")
print_separator("-")
print(f"{'Input Tokens':<30} {response_no_system.usage.input_tokens:<20} {response_with_system.usage.input_tokens:<20}")
print(f"{'Output Tokens':<30} {response_no_system.usage.output_tokens:<20} {response_with_system.usage.output_tokens:<20}")
print(f"{'Response Length (chars)':<30} {len(response_no_system.content[0].text):<20} {len(response_with_system.content[0].text):<20}")
print_separator("=")
print("\n")