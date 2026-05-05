import re
from pathlib import Path

from service import LexicalDatabaseBM25

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


###

# Main execution
if __name__ == "__main__":
    # Define the database path
    DB_PATH = "./bedrock_mantle/anthropic/repository/bm25_lexical_db.pickle"

    # Check if database exists
    db_exists = Path(DB_PATH).exists()

    if db_exists:
        print("=== Loading Existing BM25 Database ===\n")
        lexical_db = LexicalDatabaseBM25.load_from_file(DB_PATH)
        print(f"{lexical_db}\n")
    else:
        print("=== Creating New BM25 Database ===\n")

        # Load document
        print("Loading document...")
        with open("./bedrock_mantle/anthropic/data/report.md", "r") as f:
            text = f.read()

        # Chunk the document
        print("Chunking document...")
        chunks = chunk_by_section(text)
        print(f"Created {len(chunks)} chunks\n")

        # Initialize BM25 database
        lexical_db = LexicalDatabaseBM25(
            k1=1.5,  # Term frequency saturation parameter
            b=0.75   # Length normalization parameter
        )

        # Add all chunks to the database
        print("Adding chunks to BM25 index...")
        for i, chunk in enumerate(chunks):
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
            try:
                document = {
                    "content": chunk,
                    "chunk_id": i,
                    "chunk_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
                }
                lexical_db.add_document(document)
            except Exception as e:
                print(f"  ✗ Error adding chunk {i+1}: {e}")

        print(f"\n{lexical_db}")

        # Save the database
        print("\nSaving database...")
        lexical_db.save(DB_PATH)

    # Search for similar chunks using BM25
    print("\n=== Searching with BM25 (Lexical Search) ===\n")

    questions = [
        "What happened with INC-2023-Q4-001?"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 60)

        try:
            results = lexical_db.search(question, k=3)

            if not results:
                print("No results found.")
                continue

            for rank, (doc, score) in enumerate(results, 1):
                print(f"\nRank {rank} (BM25 Score: {score:.4f})")
                print(f"Chunk ID: {doc['chunk_id']}")
                print(f"Preview: {doc['chunk_preview']}")

        except Exception as e:
            print(f"Error searching: {e}")

    # Additional: Show statistics
    print("\n" + "=" * 60)
    print("=== Database Statistics ===")
    print(f"Total documents: {len(lexical_db)}")
    print(f"Average document length: {lexical_db._avg_doc_len:.2f} tokens")
    print(f"Unique terms in corpus: {len(lexical_db._doc_freqs)}")
    print(f"Index built: {lexical_db._index_built}")