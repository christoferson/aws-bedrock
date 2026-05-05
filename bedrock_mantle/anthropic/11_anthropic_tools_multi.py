import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from anthropic import AnthropicBedrockMantle
from anthropic.types import ToolParam
from anthropic.types import ToolUseBlock, TextBlock

###

def extract_all_tool_use_blocks(response):
    """Extract all ToolUseBlocks from the response."""
    tool_blocks = []
    for content in response.content:
        if isinstance(content, ToolUseBlock):
            tool_blocks.append(content)
    return tool_blocks


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


def calculate_time_difference(start_time, end_time, time_format="%H:%M:%S"):
    """Calculate the difference between two times in seconds."""
    try:
        start = datetime.strptime(start_time, time_format)
        end = datetime.strptime(end_time, time_format)
        difference = (end - start).total_seconds()
        return str(difference)
    except ValueError as e:
        return f"Error parsing time: {str(e)}"


def add_duration(base_datetime=None, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0, 
                 input_format="%Y-%m-%d %H:%M:%S", output_format="%Y-%m-%d %H:%M:%S"):
    """
    Add a duration to a datetime. If no base_datetime is provided, uses current time.

    Args:
        base_datetime: Starting datetime as string (optional, defaults to now)
        years: Number of years to add
        months: Number of months to add
        weeks: Number of weeks to add
        days: Number of days to add
        hours: Number of hours to add
        minutes: Number of minutes to add
        seconds: Number of seconds to add
        input_format: Format of the input datetime string
        output_format: Format of the output datetime string

    Returns:
        The resulting datetime as a formatted string
    """
    try:
        # Use current time if no base datetime provided
        if base_datetime is None or base_datetime == "":
            dt = datetime.now()
        else:
            dt = datetime.strptime(base_datetime, input_format)

        # Add duration using relativedelta for months/years and timedelta for the rest
        dt = dt + relativedelta(years=years, months=months)
        dt = dt + timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

        return dt.strftime(output_format)
    except ValueError as e:
        return f"Error: {str(e)}"


def set_reminder(reminder_datetime, message, datetime_format="%Y-%m-%d %H:%M:%S"):
    """
    Set a reminder for a specific datetime with a message.

    Args:
        reminder_datetime: The datetime when the reminder should trigger
        message: The reminder message
        datetime_format: Format of the datetime string

    Returns:
        Confirmation message
    """
    try:
        # Parse the datetime to validate it
        dt = datetime.strptime(reminder_datetime, datetime_format)

        # Dummy implementation - just print the reminder
        print(f"\n{'='*60}")
        print(f"🔔 REMINDER SET")
        print(f"{'='*60}")
        print(f"Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")

        return f"Reminder set successfully for {dt.strftime('%Y-%m-%d %H:%M:%S')}: {message}"
    except ValueError as e:
        return f"Error setting reminder: {str(e)}"


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

calculate_time_difference_schema = {
    "name": "calculate_time_difference",
    "description": "Calculates the time difference in seconds between two time strings",
    "input_schema": {
        "type": "object",
        "properties": {
            "start_time": {
                "type": "string",
                "description": "The start time as a string"
            },
            "end_time": {
                "type": "string",
                "description": "The end time as a string"
            },
            "time_format": {
                "type": "string",
                "description": "The format of the time strings. Uses Python's strftime format codes.",
                "default": "%H:%M:%S"
            }
        },
        "required": ["start_time", "end_time"]
    }
}

add_duration_schema = {
    "name": "add_duration",
    "description": "Adds a duration (years, months, weeks, days, hours, minutes, seconds) to a datetime. If no base datetime is provided, uses the current time.",
    "input_schema": {
        "type": "object",
        "properties": {
            "base_datetime": {
                "type": "string",
                "description": "The starting datetime as a string. If not provided or empty, uses current time."
            },
            "years": {
                "type": "integer",
                "description": "Number of years to add",
                "default": 0
            },
            "months": {
                "type": "integer",
                "description": "Number of months to add",
                "default": 0
            },
            "weeks": {
                "type": "integer",
                "description": "Number of weeks to add",
                "default": 0
            },
            "days": {
                "type": "integer",
                "description": "Number of days to add",
                "default": 0
            },
            "hours": {
                "type": "integer",
                "description": "Number of hours to add",
                "default": 0
            },
            "minutes": {
                "type": "integer",
                "description": "Number of minutes to add",
                "default": 0
            },
            "seconds": {
                "type": "integer",
                "description": "Number of seconds to add",
                "default": 0
            },
            "input_format": {
                "type": "string",
                "description": "Format of the input datetime string. Uses Python's strftime format codes.",
                "default": "%Y-%m-%d %H:%M:%S"
            },
            "output_format": {
                "type": "string",
                "description": "Format of the output datetime string. Uses Python's strftime format codes.",
                "default": "%Y-%m-%d %H:%M:%S"
            }
        },
        "required": []
    }
}

set_reminder_schema = {
    "name": "set_reminder",
    "description": "Sets a reminder for a specific date and time with a custom message",
    "input_schema": {
        "type": "object",
        "properties": {
            "reminder_datetime": {
                "type": "string",
                "description": "The date and time when the reminder should trigger, as a string"
            },
            "message": {
                "type": "string",
                "description": "The reminder message to display"
            },
            "datetime_format": {
                "type": "string",
                "description": "Format of the datetime string. Uses Python's strftime format codes.",
                "default": "%Y-%m-%d %H:%M:%S"
            }
        },
        "required": ["reminder_datetime", "message"]
    }
}

# Tool registry mapping tool names to functions
TOOL_REGISTRY = {
    "get_current_datetime": get_current_datetime,
    "calculate_time_difference": calculate_time_difference,
    "add_duration": add_duration,
    "set_reminder": set_reminder
}


def run_exchange(client, messages, tools, model="anthropic.claude-opus-4-7", max_tokens=1024, max_iterations=10):
    """
    Run a complete exchange with Claude, handling multiple tool calls until a final answer is returned.

    Args:
        client: The Anthropic client
        messages: List of message dictionaries
        tools: List of tool schemas
        model: Model name to use
        max_tokens: Maximum tokens for each response
        max_iterations: Maximum number of iterations to prevent infinite loops

    Returns:
        The final text response from Claude
    """
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=tools
        )

        print(f"Stop reason: {response.stop_reason}")

        # Check if we have tool uses
        tool_use_blocks = extract_all_tool_use_blocks(response)
        text_block = extract_text_block(response)

        # Display any text from this response
        if text_block:
            print(f"Assistant: {text_block.text}")

        # If no tool use, we have our final answer
        if not tool_use_blocks:
            if text_block:
                return text_block.text
            else:
                return "No response generated"

        # Append assistant's response with tool use(s)
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Process all tool uses and collect results
        tool_results = []
        for tool_use_block in tool_use_blocks:
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input
            print(f"Tool called: {tool_name} with arguments: {tool_input}")

            # Execute the tool
            if tool_name in TOOL_REGISTRY:
                tool_function = TOOL_REGISTRY[tool_name]
                tool_response = tool_function(**tool_input)
                print(f"Tool response: {tool_response}")
            else:
                tool_response = f"Error: Unknown tool '{tool_name}'"
                print(tool_response)

            # Add tool result to the list
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": tool_response
            })

        # Append all tool results in a single user message
        messages.append({
            "role": "user",
            "content": tool_results
        })

    return f"Maximum iterations ({max_iterations}) reached without final answer"


# Main execution
client = AnthropicBedrockMantle()

messages = [{
    "role": "user", 
    "content": "Set a reminder for me to check my email in 20 days from now. Reminder should show me the exact date and time and the weekday."
}]

tools = [get_current_datetime_schema, calculate_time_difference_schema, add_duration_schema, set_reminder_schema]

final_answer = run_exchange(client, messages, tools)

print("\n" + "="*50)
print("FINAL ANSWER:")
print(final_answer)
print("="*50)