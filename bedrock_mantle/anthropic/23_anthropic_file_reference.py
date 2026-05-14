import os
from pathlib import Path
from anthropic import AnthropicBedrockMantle
from anthropic.types import Message, ToolUseBlock, TextBlock

# Initialize client
client = AnthropicBedrockMantle()
model = "anthropic.claude-opus-4-7"

# ============================================================================
# Helper Functions
# ============================================================================

def add_user_message(messages, message):
    """Add a user message to the conversation."""
    user_message = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(user_message)


def add_assistant_message(messages, message):
    """Add an assistant message to the conversation."""
    assistant_message = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(assistant_message)


def chat(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=[],
    tools=None,
    thinking=False,
    thinking_effort="medium",
):
    """Send a chat request to Claude via Bedrock."""
    params = {
        "model": model,
        "max_tokens": 10000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if thinking:
        params["thinking"] = {
            "type": "adaptive",
        }
        params["output_config"] = {
            "effort": thinking_effort
        }

    if tools:
        params["tools"] = tools

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message


def text_from_message(message):
    """Extract text content from a message."""
    return "\n".join([block.text for block in message.content if block.type == "text"])


def upload(file_path):
    """
    Upload a file to Anthropic's file storage via Bedrock.

    Args:
        file_path: Path to the file to upload

    Returns:
        File metadata object with id, filename, size, etc.
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    mime_type_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/plain",
        ".py": "text/plain",
        ".js": "text/plain",
        ".html": "text/plain",
        ".css": "text/plain",
        ".csv": "text/csv",
        ".json": "application/json",
        ".xml": "application/xml",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    mime_type = mime_type_map.get(extension)

    if not mime_type:
        raise ValueError(f"Unknown mimetype for extension: {extension}")

    filename = path.name

    with open(file_path, "rb") as file:
        return client.beta.files.upload(file=(filename, file, mime_type))


def list_files():
    """List all uploaded files."""
    return client.beta.files.list()


def delete_file(file_id):
    """Delete a file by ID."""
    return client.beta.files.delete(file_id)


def download_file(file_id, filename=None):
    """
    Download a file by ID.

    Args:
        file_id: The ID of the file to download
        filename: Optional custom filename. If not provided, uses original filename.
    """
    file_content = client.beta.files.download(file_id)

    if not filename:
        file_metadata = get_metadata(file_id)
        file_content.write_to_file(file_metadata.filename)
    else:
        file_content.write_to_file(filename)


def get_metadata(file_id):
    """Get metadata for a file by ID."""
    return client.beta.files.retrieve_metadata(file_id)


def print_message_content(message):
    """Pretty print message content."""
    print("\n" + "="*80)
    for block in message.content:
        if block.type == "text":
            print(f"📝 Text: {block.text}")
        elif block.type == "tool_use":
            print(f"🔧 Tool Use: {block.name}")
            print(f"   Input: {block.input}")
        elif hasattr(block, 'thinking') and block.type == "thinking":
            print(f"💭 Thinking: {block.thinking[:200]}...")
    print("="*80 + "\n")


# ============================================================================
# Demo 1: Upload and Analyze a CSV File
# ============================================================================

def demo_csv_analysis():
    """Demo: Upload a CSV and ask Claude to analyze it."""
    print("\n" + "🔵"*40)
    print("DEMO 1: CSV File Analysis with Code Execution")
    print("🔵"*40 + "\n")

    # Create a sample CSV file
    sample_csv = """name,age,department,salary,years_experience
John Doe,35,Engineering,95000,8
Jane Smith,28,Marketing,72000,4
Bob Johnson,42,Engineering,110000,15
Alice Williams,31,Sales,68000,6
Charlie Brown,29,Engineering,85000,5
Diana Prince,38,Marketing,88000,10
Eve Davis,45,Sales,92000,18
Frank Miller,33,Engineering,98000,7
Grace Lee,27,Marketing,65000,3
Henry Wilson,41,Sales,105000,16"""

    with open("employees.csv", "w") as f:
        f.write(sample_csv)

    print("📤 Uploading employees.csv...")
    file_metadata = upload("employees.csv")
    print(f"✅ File uploaded successfully!")
    print(f"   File ID: {file_metadata.id}")
    print(f"   Filename: {file_metadata.filename}")
    print(f"   Size: {file_metadata.size} bytes")

    # Create conversation with file reference
    messages = []

    add_user_message(
        messages,
        [
            {
                "type": "text",
                "text": """
Analyze this employee dataset and provide insights:
1. Calculate average salary by department
2. Find correlation between years of experience and salary
3. Create a visualization showing salary distribution by department

Critical note: Every time you execute code, you're starting with a completely clean slate. 
No variables or library imports from previous executions exist. You need to redeclare/reimport all variables/libraries.
                """,
            },
            {"type": "container_upload", "file_id": file_metadata.id},
        ],
    )

    print("\n💬 Sending analysis request to Claude...")
    response = chat(
        messages, 
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
    )

    print_message_content(response)

    # Clean up
    print(f"\n🗑️  Deleting uploaded file...")
    delete_file(file_metadata.id)
    os.remove("employees.csv")
    print("✅ Cleanup complete")


# ============================================================================
# Demo 2: Upload and Query a Text Document
# ============================================================================

def demo_text_document():
    """Demo: Upload a text document and ask questions about it."""
    print("\n" + "🟢"*40)
    print("DEMO 2: Text Document Q&A")
    print("🟢"*40 + "\n")

    # Create a sample document
    sample_doc = """
COMPANY POLICY DOCUMENT
=======================

Remote Work Policy
------------------
Employees may work remotely up to 3 days per week with manager approval.
All remote workers must be available during core hours (10 AM - 3 PM EST).
Remote work equipment will be provided by the company.

Vacation Policy
---------------
- New employees: 15 days per year
- 3-5 years tenure: 20 days per year
- 5+ years tenure: 25 days per year
Unused vacation days can be carried over up to 5 days.

Health Benefits
---------------
The company provides comprehensive health insurance including:
- Medical, dental, and vision coverage
- Mental health support
- Gym membership reimbursement up to $50/month

Professional Development
------------------------
Each employee has an annual budget of $2,000 for:
- Conference attendance
- Online courses
- Professional certifications
    """

    with open("company_policy.txt", "w") as f:
        f.write(sample_doc)

    print("📤 Uploading company_policy.txt...")
    file_metadata = upload("company_policy.txt")
    print(f"✅ File uploaded successfully!")
    print(f"   File ID: {file_metadata.id}")

    # Ask questions about the document
    messages = []

    add_user_message(
        messages,
        [
            {
                "type": "text",
                "text": "What are the vacation day policies for different tenure levels? Also, what's the professional development budget?",
            },
            {"type": "container_upload", "file_id": file_metadata.id},
        ],
    )

    print("\n💬 Asking Claude about the document...")
    response = chat(messages)

    print("\n📄 Claude's Response:")
    print(text_from_message(response))

    # Follow-up question
    add_assistant_message(messages, response)
    add_user_message(
        messages,
        "Can you summarize all the benefits in bullet points?"
    )

    print("\n💬 Follow-up question...")
    response = chat(messages)

    print("\n📄 Claude's Response:")
    print(text_from_message(response))

    # Clean up
    print(f"\n🗑️  Deleting uploaded file...")
    delete_file(file_metadata.id)
    os.remove("company_policy.txt")
    print("✅ Cleanup complete")


# ============================================================================
# Demo 3: File Management Operations
# ============================================================================

def demo_file_management():
    """Demo: Upload, list, download, and delete files."""
    print("\n" + "🟡"*40)
    print("DEMO 3: File Management Operations")
    print("🟡"*40 + "\n")

    # Create sample files
    with open("notes.txt", "w") as f:
        f.write("These are my meeting notes from today.")

    with open("data.json", "w") as f:
        f.write('{"name": "Test", "value": 123}')

    print("📤 Uploading multiple files...")
    file1 = upload("notes.txt")
    file2 = upload("data.json")

    print(f"✅ Uploaded: {file1.filename} (ID: {file1.id})")
    print(f"✅ Uploaded: {file2.filename} (ID: {file2.id})")

    # List all files
    print("\n📋 Listing all uploaded files...")
    files = list_files()
    print(f"Total files: {len(files.data)}")
    for file in files.data:
        print(f"   - {file.filename} (ID: {file.id}, Size: {file.size} bytes)")

    # Get metadata
    print(f"\n🔍 Getting metadata for {file1.filename}...")
    metadata = get_metadata(file1.id)
    print(f"   Filename: {metadata.filename}")
    print(f"   Size: {metadata.size} bytes")
    print(f"   Created: {metadata.created_at}")

    # Download file
    print(f"\n⬇️  Downloading {file1.filename} as 'downloaded_notes.txt'...")
    download_file(file1.id, "downloaded_notes.txt")
    print("✅ Download complete")

    # Verify download
    with open("downloaded_notes.txt", "r") as f:
        content = f.read()
        print(f"   Content: {content}")

    # Clean up
    print("\n🗑️  Cleaning up...")
    delete_file(file1.id)
    delete_file(file2.id)
    os.remove("notes.txt")
    os.remove("data.json")
    os.remove("downloaded_notes.txt")
    print("✅ Cleanup complete")


# ============================================================================
# Demo 4: Multi-turn Conversation with File Context
# ============================================================================

def demo_multi_turn_with_file():
    """Demo: Have a multi-turn conversation referencing an uploaded file."""
    print("\n" + "🟣"*40)
    print("DEMO 4: Multi-turn Conversation with File Context")
    print("🟣"*40 + "\n")

    # Create a sample Python file
    sample_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b
    """

    with open("math_utils.py", "w") as f:
        f.write(sample_code)

    print("📤 Uploading math_utils.py...")
    file_metadata = upload("math_utils.py")
    print(f"✅ File uploaded: {file_metadata.id}")

    messages = []

    # Turn 1: Initial analysis
    print("\n💬 Turn 1: Asking for code review...")
    add_user_message(
        messages,
        [
            {
                "type": "text",
                "text": "Review this code and identify any performance issues.",
            },
            {"type": "container_upload", "file_id": file_metadata.id},
        ],
    )

    response = chat(messages)
    print("\n📄 Claude's Response:")
    print(text_from_message(response))

    # Turn 2: Ask for improvements
    print("\n💬 Turn 2: Asking for improvements...")
    add_assistant_message(messages, response)
    add_user_message(
        messages,
        "Can you rewrite the fibonacci function to be more efficient?"
    )

    response = chat(messages)
    print("\n📄 Claude's Response:")
    print(text_from_message(response))

    # Turn 3: Ask about the Calculator class
    print("\n💬 Turn 3: Asking about the Calculator class...")
    add_assistant_message(messages, response)
    add_user_message(
        messages,
        "What methods would you add to the Calculator class to make it more useful?"
    )

    response = chat(messages)
    print("\n📄 Claude's Response:")
    print(text_from_message(response))

    # Clean up
    print(f"\n🗑️  Deleting uploaded file...")
    delete_file(file_metadata.id)
    os.remove("math_utils.py")
    print("✅ Cleanup complete")


# ============================================================================
# Demo 5: File Upload with Adaptive Thinking
# ============================================================================

def demo_file_with_thinking():
    """Demo: Analyze a file using adaptive thinking."""
    print("\n" + "🔴"*40)
    print("DEMO 5: File Analysis with Adaptive Thinking")
    print("🔴"*40 + "\n")

    # Create a complex data file
    sample_data = """
Product Sales Data - Q1 2024
=============================

Week 1: Product A sold 150 units at $25 each
Week 2: Product A sold 180 units at $25 each
Week 3: Product A sold 120 units at $25 each
Week 4: Product A sold 200 units at $25 each

Week 1: Product B sold 80 units at $45 each
Week 2: Product B sold 95 units at $45 each
Week 3: Product B sold 110 units at $45 each
Week 4: Product B sold 125 units at $45 each

Marketing spend: $5,000 in Week 1, $7,500 in Week 2, $6,000 in Week 3, $8,000 in Week 4

Question: Which product has better ROI considering the marketing spend was split equally between products?
    """

    with open("sales_data.txt", "w") as f:
        f.write(sample_data)

    print("📤 Uploading sales_data.txt...")
    file_metadata = upload("sales_data.txt")
    print(f"✅ File uploaded: {file_metadata.id}")

    messages = []

    add_user_message(
        messages,
        [
            {
                "type": "text",
                "text": "Analyze this sales data and calculate which product has better ROI. Show your detailed reasoning.",
            },
            {"type": "container_upload", "file_id": file_metadata.id},
        ],
    )

    print("\n💬 Asking Claude to analyze with adaptive thinking...")
    print("🤔 Claude is thinking deeply...\n")

    response = chat(messages, thinking=True, thinking_effort="high")

    # Extract thinking if available
    thinking_content = None
    for block in response.content:
        if hasattr(block, 'thinking') and block.type == "thinking":
            thinking_content = block.thinking
            break

    if thinking_content:
        print("-" * 80)
        print("THINKING PROCESS:")
        print("-" * 80)
        print(thinking_content)
        print("\n" + "-" * 80)
        print("FINAL ANSWER:")
        print("-" * 80)

    print(text_from_message(response))

    # Clean up
    print(f"\n🗑️  Deleting uploaded file...")
    delete_file(file_metadata.id)
    os.remove("sales_data.txt")
    print("✅ Cleanup complete")


# ============================================================================
# Demo 6: Image Upload and Analysis
# ============================================================================

def demo_image_upload():
    """Demo: Upload and analyze an image (if you have one)."""
    print("\n" + "🟠"*40)
    print("DEMO 6: Image Upload and Analysis")
    print("🟠"*40 + "\n")

    print("Note: This demo requires an actual image file.")
    print("To test image upload:")
    print("1. Place an image file (e.g., 'test_image.jpg') in the current directory")
    print("2. Uncomment and run the code below")
    print()

    # Uncomment to test with your own image:
    """
    image_path = "test_image.jpg"

    if os.path.exists(image_path):
        print(f"📤 Uploading {image_path}...")
        file_metadata = upload(image_path)
        print(f"✅ File uploaded: {file_metadata.id}")

        messages = []
        add_user_message(
            messages,
            [
                {
                    "type": "text",
                    "text": "Describe what you see in this image in detail.",
                },
                {"type": "container_upload", "file_id": file_metadata.id},
            ],
        )

        print("\n💬 Asking Claude to analyze the image...")
        response = chat(messages)

        print("\n📄 Claude's Response:")
        print(text_from_message(response))

        # Clean up
        print(f"\n🗑️  Deleting uploaded file...")
        delete_file(file_metadata.id)
        print("✅ Cleanup complete")
    else:
        print(f"❌ Image file '{image_path}' not found")
    """


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("ANTHROPIC FILE UPLOAD & REFERENCE DEMO")
    print("Using AnthropicBedrockMantle with AWS Bedrock")
    print("="*80)

    try:
        # Run all demos
        demo_csv_analysis()
        demo_text_document()
        demo_file_management()
        demo_multi_turn_with_file()
        demo_file_with_thinking()
        demo_image_upload()

        print("\n" + "="*80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nKey Features Demonstrated:")
        print("  ✓ File upload (CSV, TXT, JSON, images)")
        print("  ✓ File reference in messages (container_upload)")
        print("  ✓ Code execution tool with file analysis")
        print("  ✓ Multi-turn conversations with file context")
        print("  ✓ File management (list, download, delete)")
        print("  ✓ Adaptive thinking with file analysis")
        print("  ✓ File metadata retrieval")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()