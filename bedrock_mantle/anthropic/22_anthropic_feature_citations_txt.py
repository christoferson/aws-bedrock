import base64
from pathlib import Path
from anthropic import AnthropicBedrockMantle

###
# TEXT FILE HELPERS
###

def read_text_file(file_path: str) -> str:
    """Read a text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_text_with_citations(client, text_path: str, question: str, enable_citations: bool = False):
    """
    Read and analyze a text document.

    Args:
        client: AnthropicBedrockMantle client
        text_path: Path to the text file
        question: Question to ask about the document
        enable_citations: Whether to enable citations

    Returns:
        Response message
    """
    text_content = read_text_file(text_path)

    content = [
        {
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": text_content,
            },
            "title": Path(text_path).stem,
            "citations": {"enabled": enable_citations},
        },
        {
            "type": "text",
            "text": question,
        },
    ]

    response = client.messages.create(
        model="anthropic.claude-opus-4-7",
        max_tokens=4000,
        messages=[{"role": "user", "content": content}]
    )

    return response


def print_response(response):
    """Print the response text."""
    for block in response.content:
        if block.type == "text":
            print(block.text)


def print_response_with_citations(response):
    """Print the response text and citation information with character positions."""
    # Print the main text first
    print("RESPONSE:")
    print("-" * 80)
    for block in response.content:
        if block.type == "text":
            print(block.text)

    # Print citations
    print("\n" + "="*80)
    print("CITATIONS:")
    print("="*80)

    citation_count = 0
    for block in response.content:
        if block.type == "text" and hasattr(block, 'citations') and block.citations:
            for citation in block.citations:
                citation_count += 1
                print(f"\n[Citation {citation_count}]")
                print(f"  Type: {citation.type}")
                print(f"  Document: {citation.document_title}")

                # For char_location type (text files)
                if citation.type == "char_location":
                    if hasattr(citation, 'start_char_index'):
                        print(f"  Character Position: {citation.start_char_index} - {citation.end_char_index}")

                # For page_location type (PDFs)
                elif citation.type == "page_location":
                    if hasattr(citation, 'start_page_number'):
                        print(f"  Pages: {citation.start_page_number} - {citation.end_page_number}")

                print(f"  Cited Text: \"{citation.cited_text.strip()}\"")

                # Show document index
                if hasattr(citation, 'document_index'):
                    print(f"  Document Index: {citation.document_index}")

    if citation_count == 0:
        print("\nNo citations found in response.")


###
# DEMOS
###

def demo_read_text(client, text_path: str):
    """Demo: Read text without citations."""
    print("\n" + "="*80)
    print("=== DEMO 1: Read Text (No Citations) ===")
    print("="*80 + "\n")

    question = "Summarize the key topics covered in this study guide."
    print(f"Text File: {text_path}")
    print(f"Question: {question}\n")
    print("-" * 80 + "\n")

    response = read_text_with_citations(client, text_path, question, enable_citations=False)
    print_response(response)
    print()


def demo_read_text_with_citations(client, text_path: str):
    """Demo: Read text with citations showing character positions."""
    print("\n" + "="*80)
    print("=== DEMO 2: Read Text with Citations (Character Positions) ===")
    print("="*80 + "\n")

    question = "What are the key aspects of tool descriptions according to this guide?"
    print(f"Text File: {text_path}")
    print(f"Question: {question}\n")
    print("-" * 80 + "\n")

    response = read_text_with_citations(client, text_path, question, enable_citations=True)
    print_response_with_citations(response)
    print()


###
# MAIN
###

if __name__ == "__main__":
    import sys

    client = AnthropicBedrockMantle()

    print("="*80)
    print("TEXT ANALYSIS DEMOS")
    print("="*80)

    # Get text file path
    text_path = sys.argv[1] if len(sys.argv) > 1 else "./bedrock_mantle/anthropic/data/documents/guide.md"

    if not Path(text_path).exists():
        print(f"Error: Text file not found at {text_path}")
        sys.exit(1)

    # Run demos
    demo_read_text(client, text_path)
    demo_read_text_with_citations(client, text_path)

    print("="*80)
    print("Done!")
    print("="*80)