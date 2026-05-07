from markitdown import MarkItDown, StreamInfo
from io import BytesIO
import os
from pydantic import Field


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    file_path: str = Field(description="Path to the PDF or DOCX file to convert to markdown")
) -> str:
    """Convert a PDF or DOCX file to markdown-formatted text.

    Reads a document file from the specified path and converts its contents
    to markdown format. Supports PDF and DOCX file formats.

    When to use:
    - When you have a file path to a document that needs to be converted
    - When working with local PDF or DOCX files
    - When you need to extract and format document content as markdown

    When not to use:
    - When you already have binary document data (use binary_document_to_markdown instead)
    - For file formats other than PDF or DOCX

    Examples:
    >>> document_path_to_markdown("/path/to/document.pdf")
    "# Document Title\\n\\nDocument content here..."
    >>> document_path_to_markdown("/path/to/report.docx")
    "# Report\\n\\n## Section 1\\n\\nReport content..."
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Extract and validate file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower().lstrip('.')

    if ext not in ['pdf', 'docx']:
        raise ValueError(f"Unsupported file type: .{ext}. Only PDF and DOCX files are supported.")

    # Read file as binary
    with open(file_path, 'rb') as f:
        binary_data = f.read()

    # Convert using existing function
    return binary_document_to_markdown(binary_data, ext)
