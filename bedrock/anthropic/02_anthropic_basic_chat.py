import logging
import boto3

client = boto3.client("bedrock-runtime", region_name="us-west-2")
model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"


def add_user_message(messages, text):
    user_message = {"role": "user", "content": [{"text": text}]}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": [{"text": text}]}
    messages.append(assistant_message)


def chat(messages):
    response = client.converse(modelId=model_id, messages=messages)
    print(response)
    return response["output"]["message"]["content"][0]["text"]


messages = []

while True:
    # Get user input
    user_input = input("> ")
    #print(f"> {user_input}")
    if user_input.lower() in ["/exit", "/quit"]:
        break

    # Add user's input to list of messages
    add_user_message(messages, user_input)
    # Send list of messages to the API
    text = chat(messages)
    # Add generated text to list of messages
    add_assistant_message(messages, text)
    # Print the generated text
    print(text)