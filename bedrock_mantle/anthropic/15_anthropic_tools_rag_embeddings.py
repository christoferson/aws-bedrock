import logging
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from anthropic import AnthropicBedrockMantle
from anthropic.types import ToolParam
from anthropic.types import ToolUseBlock, TextBlock
import boto3
import json

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


def generate_embedding(text, model_id="amazon.titan-embed-text-v1", region_name="us-east-1"):
    """
    Generate embeddings using Amazon Bedrock Titan Embeddings model.

    Args:
        text: The input text to generate embeddings for
        model_id: The Bedrock model ID (default: amazon.titan-embed-text-v1)
        region_name: AWS region name (default: us-east-1)

    Returns:
        List of floats representing the embedding vector
    """
    # Initialize Bedrock runtime client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=region_name
    )

    # Prepare the request body
    body = json.dumps({
        "inputText": text
    })

    # Invoke the model
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=body
    )

    # Parse the response
    response_body = json.loads(response['body'].read())
    embedding = response_body.get('embedding')

    return embedding


def generate_embeddings_batch(texts, model_id="amazon.titan-embed-text-v1", region_name="us-east-1"):
    """
    Generate embeddings for multiple texts.

    Args:
        texts: List of input texts to generate embeddings for
        model_id: The Bedrock model ID (default: amazon.titan-embed-text-v1)
        region_name: AWS region name (default: us-east-1)

    Returns:
        List of embedding vectors
    """
    embeddings = []
    for text in texts:
        embedding = generate_embedding(text, model_id, region_name)
        embeddings.append(embedding)
    return embeddings

###


with open("./bedrock_mantle/anthropic/data/report.md", "r") as f:
    text = f.read()

#chunks = chunk_by_char(text, 300, 100)
#chunks = chunk_by_sentence(text)
chunks = chunk_by_section(text)

print("=== Chunks ===\n")
[print(chunk + "\n----\n") for chunk in chunks]

# Generate embedding for the first chunk
print("\n=== Generating Embedding for First Chunk ===\n")
first_chunk = chunks[0]
print(f"First chunk text (first 200 chars):\n{first_chunk[:200]}...\n")

try:
    embedding = generate_embedding(first_chunk)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 10 values of embedding: {embedding[:10]}")
    print(f"\nFull embedding:\n{embedding}")
except Exception as e:
    print(f"Error generating embedding: {e}")
    print("\nMake sure you have:")
    print("1. AWS credentials configured")
    print("2. Access to Amazon Bedrock")
    print("3. Titan Embeddings model enabled in your AWS account")