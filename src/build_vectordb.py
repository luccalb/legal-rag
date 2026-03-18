"""
Vector Database Setup
Processes scraped BGB sections and stores them in ChromaDB
"""
import os
import json
from typing import List, Dict
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

load_dotenv()

# Disable ChromaDB telemetry to avoid warnings
os.environ['CHROMA_TELEMETRY_ENABLED'] = 'false'


class VectorDBManager:
    def __init__(self):
        self.db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        self.collection_name = os.getenv("COLLECTION_NAME", "bgb_erbrecht")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "900"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))

        # Initialize embeddings
        print(f"Initializing embeddings with model: {self.embedding_model}")
        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model,
            base_url=self.ollama_base_url
        )

    def load_sections(self, filepath: str = "data/bgb_all.json") -> List[Dict[str, str]]:
        """Load scraped sections from JSON file"""
        print(f"Loading sections from {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            sections = json.load(f)
        print(f"Loaded {len(sections)} sections")
        return sections

    def sections_to_documents(self, sections: List[Dict[str, str]]) -> List[Document]:
        """Convert sections to LangChain Document objects"""
        documents = []

        for section in sections:
            # Combine section number, title, and content
            section_num = section.get('section', '')
            title = section.get('title', '')
            content = section.get('content', '')

            # Create full text
            if title:
                full_text = f"{section_num} {title}\n\n{content}"
            else:
                full_text = f"{section_num}\n\n{content}"

            # Create document with metadata
            doc = Document(
                page_content=full_text.strip(),
                metadata={
                    'section': section_num,
                    'title': title,
                    'source': 'BGB'
                }
            )
            documents.append(doc)

        print(f"Created {len(documents)} documents")
        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into consistent chunks for embedding and retrieval.
        Preserves section metadata in all chunks.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunked_docs = []
        for doc in documents:
            chunks = text_splitter.split_documents([doc])
            # Preserve metadata in all chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_index'] = i
                chunk.metadata['total_chunks'] = len(chunks)
            chunked_docs.extend(chunks)

        print(f"Split {len(documents)} documents into {len(chunked_docs)} chunks")
        return chunked_docs

    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """Create and persist ChromaDB vector store"""
        print(f"Creating vector store at {self.db_path}...")
        print("This may take a few minutes for embedding generation...")

        # Ensure directory exists
        os.makedirs(self.db_path, exist_ok=True)

        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.db_path
        )

        print(f"✓ Vector store created with {len(documents)} documents")
        return vectorstore

    def load_vector_store(self) -> Chroma:
        """Load existing vector store"""
        print(f"Loading vector store from {self.db_path}...")
        vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.db_path
        )
        print("✓ Vector store loaded")
        return vectorstore

    def build_database(self, sections_file: str = "data/bgb_all.json"):
        """Main method to build the vector database from scraped sections"""
        # Load sections
        sections = self.load_sections(sections_file)

        if not sections:
            raise ValueError("No sections found in the data file")

        # Convert to documents
        documents = self.sections_to_documents(sections)

        # Chunk documents to fit within embedding model's context length
        # This prevents "input length exceeds context length" errors
        documents = self.chunk_documents(documents)

        # Create vector store
        vectorstore = self.create_vector_store(documents)

        # Test query
        print("\nTesting vector store with sample query...")
        results = vectorstore.similarity_search("Wer erbt?", k=2)
        print(f"Found {len(results)} results")
        if results:
            print(f"Top result: {results[0].metadata.get('section', 'Unknown')}")

        return vectorstore


def main():
    """Main entry point for building vector database"""
    manager = VectorDBManager()

    try:
        print("=" * 60)
        print("Building Vector Database for BGB")
        print("=" * 60)

        vectorstore = manager.build_database()

        print("\n" + "=" * 60)
        print("✓ Vector database built successfully!")
        print(f"✓ Database location: {manager.db_path}")
        print(f"✓ Collection name: {manager.collection_name}")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error building vector database: {e}")
        raise


if __name__ == "__main__":
    main()
