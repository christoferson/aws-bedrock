import re
from pathlib import Path
import boto3
import json
from typing import List, Dict, Any, Tuple

from service import VectorDatabase
from service import LexicalDatabaseBM25
from service import HybridDatabase

###
# UTILITY FUNCTIONS
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
# DATABASE MANAGEMENT
###

def load_or_create_databases(
    vector_db_path: str,
    bm25_db_path: str,
    document_path: str,
    embedding_fn
) -> Tuple[VectorDatabase, LexicalDatabaseBM25]:
    """Load existing databases or create new ones from document."""
    vector_db_exists = Path(vector_db_path).exists()
    bm25_db_exists = Path(bm25_db_path).exists()

    if vector_db_exists and bm25_db_exists:
        print("=== Loading Existing Databases ===\n")
        vector_db = VectorDatabase.load_from_file(vector_db_path, embedding_fn=embedding_fn)
        bm25_db = LexicalDatabaseBM25.load_from_file(bm25_db_path)
        print(f"Vector DB: {vector_db}")
        print(f"BM25 DB: {bm25_db}\n")
    else:
        print("=== Creating New Databases ===\n")

        # Load document
        print("Loading document...")
        with open(document_path, "r") as f:
            text = f.read()

        # Chunk the document
        print("Chunking document...")
        chunks = chunk_by_section(text)
        print(f"Created {len(chunks)} chunks\n")

        # Initialize databases
        print("Initializing Vector Database...")
        vector_db = VectorDatabase(
            distance_metric="cosine",
            embedding_fn=embedding_fn
        )

        print("Initializing BM25 Database...")
        bm25_db = LexicalDatabaseBM25(k1=1.5, b=0.75)

        # Prepare documents
        print("\nPreparing documents...")
        documents = []
        for i, chunk in enumerate(chunks):
            document = {
                "content": chunk,
                "chunk_id": i,
                "chunk_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
            }
            documents.append(document)

        # Add documents to Vector Database
        print("\nAdding documents to Vector Database...")
        print("(This may take a while due to embedding generation)")
        for i, doc in enumerate(documents, 1):
            print(f"  Processing chunk {i}/{len(documents)}...", end='\r')
            vector_db.add_document(doc)
        print(f"\n✓ Added {len(documents)} documents to Vector DB")

        # Add documents to BM25 Database
        print("\nAdding documents to BM25 Database...")
        for i, doc in enumerate(documents, 1):
            print(f"  Processing chunk {i}/{len(documents)}...", end='\r')
            bm25_db.add_document(doc)
        print(f"\n✓ Added {len(documents)} documents to BM25 DB")

        print(f"\nVector DB: {vector_db}")
        print(f"BM25 DB: {bm25_db}")

        # Save the databases
        print("\nSaving databases...")
        vector_db.save(vector_db_path)
        bm25_db.save(bm25_db_path)

    return vector_db, bm25_db


###
# SEARCH DEMOS
###

def run_hybrid_search_demo(hybrid_db: HybridDatabase, questions: List[str]):
    """Run hybrid search demo with multiple questions."""
    print("\n" + "="*80)
    print("=== HYBRID SEARCH: BM25 + Vector with RRF ===")
    print("="*80 + "\n")

    for question in questions:
        print(f"\n{'='*80}")
        print(f"Question: {question}")
        print('='*80)

        try:
            results = hybrid_db.search(question, k=3, k_rrf=60)

            if not results:
                print("No results found.")
                continue

            for rank, (doc, score) in enumerate(results, 1):
                print(f"\n--- Rank {rank} (RRF Score: {score:.6f}) ---")
                print(f"Chunk ID: {doc['chunk_id']}")
                print(f"Preview: {doc['chunk_preview']}")

        except Exception as e:
            print(f"✗ Error searching: {e}")


def run_comparison_demo(
    bm25_db: LexicalDatabaseBM25,
    vector_db: VectorDatabase,
    hybrid_db: HybridDatabase,
    test_question: str
):
    """Run comparison demo showing all three search methods."""
    print("\n\n" + "="*80)
    print("=== COMPARISON: Individual vs Hybrid Results ===")
    print("="*80 + "\n")
    print(f"Test Question: {test_question}\n")

    # BM25 Results
    print("-" * 80)
    print("BM25 (Lexical) Results:")
    print("-" * 80)
    try:
        bm25_results = bm25_db.search(test_question, k=5)
        for rank, (doc, score) in enumerate(bm25_results, 1):
            print(f"{rank}. Chunk {doc['chunk_id']:2d} | Score: {score:8.4f} | {doc['chunk_preview'][:60]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Vector Results
    print("\n" + "-" * 80)
    print("Vector (Semantic) Results:")
    print("-" * 80)
    try:
        vector_results = vector_db.search(test_question, k=5)
        for rank, (doc, distance) in enumerate(vector_results, 1):
            print(f"{rank}. Chunk {doc['chunk_id']:2d} | Distance: {distance:.4f} | {doc['chunk_preview'][:60]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Hybrid Results
    print("\n" + "-" * 80)
    print("Hybrid (BM25 + Vector with RRF) Results:")
    print("-" * 80)
    try:
        hybrid_results = hybrid_db.search(test_question, k=5, k_rrf=60)
        for rank, (doc, score) in enumerate(hybrid_results, 1):
            print(f"{rank}. Chunk {doc['chunk_id']:2d} | RRF Score: {score:.6f} | {doc['chunk_preview'][:60]}...")
    except Exception as e:
        print(f"Error: {e}")


def display_analysis():
    """Display analysis of different search methods."""
    print("\n\n" + "="*80)
    print("=== ANALYSIS ===")
    print("="*80)
    print("""
BM25 (Lexical Search):
  • Strengths: Exact keyword matching, good for specific terms/IDs
  • Best for: Queries with unique identifiers (e.g., "INC-2023-Q4-001")

Vector (Semantic Search):
  • Strengths: Understanding meaning and context
  • Best for: Conceptual queries (e.g., "main findings", "recommendations")

Hybrid (RRF Fusion):
  • Combines both approaches using Reciprocal Rank Fusion
  • Balances keyword matching with semantic understanding
  • More robust across different query types
  • k_rrf parameter (default=60) controls fusion behavior
    """)


###
# MAIN EXECUTION
###

if __name__ == "__main__":
    # Configuration
    DB_PATH_VECTOR = "./bedrock_mantle/anthropic/repository/vectordb_cosine.pickle"
    DB_PATH_BM25 = "./bedrock_mantle/anthropic/repository/bm25_index.pickle"
    DOCUMENT_PATH = "./bedrock_mantle/anthropic/data/report.md"

    # Load or create databases
    vector_db, bm25_db = load_or_create_databases(
        DB_PATH_VECTOR,
        DB_PATH_BM25,
        DOCUMENT_PATH,
        generate_embedding
    )

    # Create hybrid database
    print("=== Creating Hybrid Database (BM25 + Vector) ===\n")
    hybrid_db = HybridDatabase(bm25_db, vector_db)
    print("✓ Hybrid database created with BM25 (lexical) and Vector (semantic) indexes\n")

    # Define test questions
    questions = [
        #"What are the main findings of the report?",
        #"What recommendations are provided?",
        #"What is the conclusion?",
        #"What did the software engineering department do last year?",
        "What happened with INC-2023-Q4-001?"
    ]

    # Run demos
    run_hybrid_search_demo(hybrid_db, questions)
    run_comparison_demo(bm25_db, vector_db, hybrid_db, "What happened with INC-2023-Q4-001?")
    display_analysis()

    # Completion
    print("\n" + "="*80)
    print("Search complete!")
    print("="*80)