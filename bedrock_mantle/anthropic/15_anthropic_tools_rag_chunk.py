import logging
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from anthropic import AnthropicBedrockMantle
from anthropic.types import ToolParam
from anthropic.types import ToolUseBlock, TextBlock


###

def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    """
    Split text into chunks of a fixed character length with optional overlap.

    Args:
        text: The input text to chunk
        chunk_size: Maximum number of characters per chunk (default: 150)
        chunk_overlap: Number of characters to overlap between chunks (default: 20)

    Returns:
        List of text chunks
    """
    chunks = []
    start_idx = 0

    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunk_text = text[start_idx:end_idx]
        chunks.append(chunk_text)

        # Move start position, accounting for overlap
        start_idx = end_idx - chunk_overlap if end_idx < len(text) else len(text)

    return chunks


def chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1):
    """
    Split text into chunks based on sentence boundaries.

    Args:
        text: The input text to chunk
        max_sentences_per_chunk: Maximum number of sentences per chunk (default: 5)
        overlap_sentences: Number of sentences to overlap between chunks (default: 1)

    Returns:
        List of text chunks
    """
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    start_idx = 0

    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        current_chunk = sentences[start_idx:end_idx]
        chunks.append(" ".join(current_chunk))

        # Move forward by chunk size minus overlap
        start_idx += max_sentences_per_chunk - overlap_sentences

    return chunks


def chunk_by_section(document_text):
    """
    Split text into chunks based on markdown section headers (## ).

    Args:
        document_text: The input text to chunk (markdown formatted)

    Returns:
        List of text chunks, one per section
    """
    pattern = r"\n## "
    return re.split(pattern, document_text)

###


with open("./bedrock_mantle/anthropic/data/report.md", "r") as f:
    text = f.read()

#chunks = chunk_by_char(text, 300, 100)
#chunks = chunk_by_sentence(text)
chunks = chunk_by_section(text)

[print(chunk + "\n----\n") for chunk in chunks]
