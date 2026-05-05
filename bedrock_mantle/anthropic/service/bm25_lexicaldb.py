import math
import pickle
import re
from collections import Counter
from typing import Callable, Optional, Any, List, Dict, Tuple


class LexicalDatabaseBM25:
    """BM25-based lexical search database for document retrieval."""

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        tokenizer: Optional[Callable[[str], List[str]]] = None,
    ):
        self.documents: List[Dict[str, Any]] = []
        self._corpus_tokens: List[List[str]] = []
        self._doc_len: List[int] = []
        self._doc_freqs: Dict[str, int] = {}
        self._avg_doc_len: float = 0.0
        self._idf: Dict[str, float] = {}
        self._index_built: bool = False

        self.k1 = k1
        self.b = b
        self._tokenizer = tokenizer if tokenizer else self._default_tokenizer

    def _default_tokenizer(self, text: str) -> List[str]:
        """Default tokenizer: lowercase and split on non-word characters."""
        text = text.lower()
        tokens = re.split(r"\W+", text)
        return [token for token in tokens if token]

    def _update_stats_add(self, doc_tokens: List[str]):
        """Update statistics when adding a document."""
        self._doc_len.append(len(doc_tokens))

        seen_in_doc = set()
        for token in doc_tokens:
            if token not in seen_in_doc:
                self._doc_freqs[token] = self._doc_freqs.get(token, 0) + 1
                seen_in_doc.add(token)

        self._index_built = False

    def _calculate_idf(self):
        """Calculate IDF scores for all terms."""
        N = len(self.documents)
        self._idf = {}
        for term, freq in self._doc_freqs.items():
            idf_score = math.log(((N - freq + 0.5) / (freq + 0.5)) + 1)
            self._idf[term] = idf_score

    def _build_index(self):
        """Build the BM25 index."""
        if not self.documents:
            self._avg_doc_len = 0.0
            self._idf = {}
            self._index_built = True
            return

        self._avg_doc_len = sum(self._doc_len) / len(self.documents)
        self._calculate_idf()
        self._index_built = True

    def add_document(self, document: Dict[str, Any]):
        """
        Add a document to the index.

        Args:
            document: Dictionary with at least a 'content' key containing the text
        """
        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary.")
        if "content" not in document:
            raise ValueError(
                "Document dictionary must contain a 'content' key."
            )

        content = document.get("content", "")
        if not isinstance(content, str):
            raise TypeError("Document 'content' must be a string.")

        doc_tokens = self._tokenizer(content)

        self.documents.append(document)
        self._corpus_tokens.append(doc_tokens)
        self._update_stats_add(doc_tokens)

    def _compute_bm25_score(
        self, query_tokens: List[str], doc_index: int
    ) -> float:
        """Compute BM25 score for a document given query tokens."""
        score = 0.0
        doc_term_counts = Counter(self._corpus_tokens[doc_index])
        doc_length = self._doc_len[doc_index]

        for token in query_tokens:
            if token not in self._idf:
                continue

            idf = self._idf[token]
            term_freq = doc_term_counts.get(token, 0)

            numerator = idf * term_freq * (self.k1 + 1)
            denominator = term_freq + self.k1 * (
                1 - self.b + self.b * (doc_length / self._avg_doc_len)
            )
            score += numerator / (denominator + 1e-9)

        return score

    def search(
        self,
        query_text: str,
        k: int = 1,
        return_scores: bool = True,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for documents matching the query.

        Args:
            query_text: The search query
            k: Number of top results to return
            return_scores: If True, return raw BM25 scores; if False, return normalized scores

        Returns:
            List of tuples (document, score) sorted by relevance
        """
        if not self.documents:
            return []

        if not isinstance(query_text, str):
            raise TypeError("Query text must be a string.")

        if k <= 0:
            raise ValueError("k must be a positive integer.")

        if not self._index_built:
            self._build_index()

        if self._avg_doc_len == 0:
            return []

        query_tokens = self._tokenizer(query_text)
        if not query_tokens:
            return []

        # Compute scores for all documents
        scored_docs = []
        for i in range(len(self.documents)):
            score = self._compute_bm25_score(query_tokens, i)
            if score > 1e-9:
                scored_docs.append((score, self.documents[i]))

        # Sort by score (descending)
        scored_docs.sort(key=lambda item: item[0], reverse=True)

        # Return top k results
        results = []
        for score, doc in scored_docs[:k]:
            results.append((doc, score))

        return results

    def save(self, filepath: str):
        """
        Save the BM25 index to a file.

        Args:
            filepath: Path to save the pickle file
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f"✓ BM25 index saved to {filepath}")

    @classmethod
    def load_from_file(cls, filepath: str) -> 'LexicalDatabaseBM25':
        """
        Load a BM25 index from a file.

        Args:
            filepath: Path to the pickle file

        Returns:
            Loaded LexicalDatabaseBM25 instance
        """
        with open(filepath, 'rb') as f:
            instance = pickle.load(f)
        print(f"✓ BM25 index loaded from {filepath}")
        return instance

    def __len__(self) -> int:
        """Return the number of documents in the index."""
        return len(self.documents)

    def __repr__(self) -> str:
        """String representation of the BM25 index."""
        return (
            f"LexicalDatabaseBM25("
            f"documents={len(self)}, "
            f"k1={self.k1}, "
            f"b={self.b}, "
            f"index_built={self._index_built})"
        )