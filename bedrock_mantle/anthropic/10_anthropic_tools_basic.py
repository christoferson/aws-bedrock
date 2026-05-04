import logging
from datetime import datetime
from anthropic import AnthropicBedrockMantle
from anthropic.types import ToolParam
from anthropic.types import ToolUseBlock, TextBlock

###

def extract_tool_use_block(response):
    """Extract the first ToolUseBlock from the response."""
    for content in response.content:
        if isinstance(content, ToolUseBlock):
            return content
    return None


def extract_text_block(response):
    """Extract the first TextBlock from the response."""
    for content in response.content:
        if isinstance(content, TextBlock):
            return content
    return None

###

def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)

get_current_datetime_schema = {
    "name": "get_current_datetime",
    "description": "Returns the current date and time formatted according to the specified format",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "A string specifying the format of the returned datetime. Uses Python's strftime format codes.",
                "default": "%Y-%m-%d %H:%M:%S"
            }
        },
        "required": []
    }
}


client = AnthropicBedrockMantle()

messages=[{"role": "user", "content": "What is the current time in 12-hour format?"}]

response = client.messages.create(
    model="anthropic.claude-opus-4-7",
    max_tokens=256,
    messages=messages,
    tools=[get_current_datetime_schema]
)

#print(response)
#print(response.content[0])

text_block = extract_text_block(response)
tool_use_block = extract_tool_use_block(response)

if text_block:
    print(f"Text: {text_block.text}")

if tool_use_block:
    tool_name = tool_use_block.name
    tool_input = tool_use_block.input
    print(f"Tool called: {tool_name} with arguments: {tool_input}")

    if tool_name == "get_current_datetime":
        tool_response = get_current_datetime(**tool_input)
        print(f"Tool response: {tool_response}")

        # Append assistant's response with tool use
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Append tool result
        messages.append({
            "role": "user", 
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": tool_response
            }]
        })

        #print(messages)

        # Get final response from Claude
        final_response = client.messages.create(
            model="anthropic.claude-opus-4-7",
            max_tokens=256,
            messages=messages,
            tools=[get_current_datetime_schema]
        )

        final_text = extract_text_block(final_response)
        if final_text:
            print(f"\nFinal Response: {final_text.text}")
