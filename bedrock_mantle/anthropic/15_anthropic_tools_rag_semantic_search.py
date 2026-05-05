import re
from pathlib import Path
import boto3
import json

from service import VectorDatabase

###

def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    """Split text into chunks of a fixed character length with optional overlap."""
    chunks = []
    start_idx = 0

    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunk_text = text[start_idx:end_idx]
        chunks.append(chunk_text)
        start_idx = end_idx - chunk_overlap if end_idx < len(text) else len(text)

    return chunks


def chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1):
    """Split text into chunks based on sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    start_idx = 0

    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        current_chunk = sentences[start_idx:end_idx]
        chunks.append(" ".join(current_chunk))
        start_idx += max_sentences_per_chunk - overlap_sentences

    return chunks


def chunk_by_section(document_text):
    """Split text into chunks based on markdown section headers (## )."""
    pattern = r"\n## "
    return re.split(pattern, document_text)


def generate_embedding(text, model_id="amazon.titan-embed-text-v1", region_name="us-east-1"):
    """Generate embeddings using Amazon Bedrock Titan Embeddings model."""
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=region_name
    )

    body = json.dumps({"inputText": text})

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=body
    )

    response_body = json.loads(response['body'].read())
    embedding = response_body.get('embedding')

    return embedding


###

# Main execution
if __name__ == "__main__":
    # Define the database path
    DB_PATH = "./bedrock_mantle/anthropic/repository/simple_vectordb.pickle"

    # Check if database exists
    db_exists = Path(DB_PATH).exists()

    if db_exists:
        print("=== Loading Existing Vector Database ===\n")
        vector_db = VectorDatabase.load_from_file(DB_PATH, embedding_fn=generate_embedding)
        print(f"{vector_db}\n")
    else:
        print("=== Creating New Vector Database ===\n")

        # Load document
        print("Loading document...")
        with open("./bedrock_mantle/anthropic/data/report.md", "r") as f:
            text = f.read()

        # Chunk the document
        print("Chunking document...")
        chunks = chunk_by_section(text)
        print(f"Created {len(chunks)} chunks\n")

        # Initialize vector database
        vector_db = VectorDatabase(
            distance_metric="cosine",
            embedding_fn=generate_embedding
        )

        # Add all chunks to the database
        print("Generating embeddings and adding to database...")
        for i, chunk in enumerate(chunks):
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
            try:
                document = {
                    "content": chunk,
                    "chunk_id": i,
                    "chunk_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
                }
                vector_db.add_document(document)
            except Exception as e:
                print(f"  ✗ Error adding chunk {i+1}: {e}")

        print(f"\n{vector_db}")

        # Save the database
        print("\nSaving database...")
        vector_db.save(DB_PATH)

    # Search for similar chunks
    print("\n=== Searching for Similar Chunks ===\n")

    questions = [
        #"What are the main findings of the report?",
        #"What recommendations are provided?",
        #"What is the conclusion?",
        #"What did the software engineering department do last year?",
        "What happened with INC-2023-Q4-001?"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 60)

        try:
            results = vector_db.search(question, k=3)

            for rank, (doc, distance) in enumerate(results, 1):
                print(f"\nRank {rank} (Distance: {distance:.4f})")
                print(f"Chunk ID: {doc['chunk_id']}")
                print(f"Preview: {doc['chunk_preview']}")

        except Exception as e:
            print(f"Error searching: {e}")