"""
RAG Chain Implementation
Implements the RetrievalQA chain for querying German Civil Code (BGB)
"""
import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

# Disable ChromaDB telemetry to avoid warnings
os.environ['CHROMA_TELEMETRY_ENABLED'] = 'false'


class BGBQueryEngine:
    def __init__(self):
        self.db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        self.collection_name = os.getenv("COLLECTION_NAME", "bgb_erbrecht")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral:latest")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.top_k = int(os.getenv("TOP_K_RESULTS", "10"))
        self.rewrite_min_words = int(os.getenv("REWRITE_QUERY_MIN_WORDS", "8"))

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", None)

        # Initialize components
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None

    def initialize(self):
        """Initialize all components of the RAG chain"""
        print("Initializing RAG components...")

        # Initialize embeddings
        print(f"Loading embeddings model: {self.embedding_model}")
        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model,
            base_url=self.ollama_base_url
        )

        # Load vector store
        print(f"Loading vector store from: {self.db_path}")
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.db_path
        )

        if self.gemini_api_key:
            print("Using Gemini API Key for LLM access")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.1,
                google_api_key=self.gemini_api_key
            )
        else:
            # Initialize LLM
            print(f"Initializing LLM: {self.ollama_model}")
            self.llm = Ollama(
                model=self.ollama_model,
                base_url=self.ollama_base_url,
                temperature=0.1  # Low temperature for more factual responses
            )

        # Create custom prompt template
        prompt_template = """Du bist ein Rechtsexperte für deutsches Zivilrecht (BGB). Deine Aufgabe ist es, Fragen zum BGB ausschließlich auf Basis der bereitgestellten Gesetzestexte zu beantworten.

        WICHTIGE REGELN:
        1. Beantworte die Frage NUR anhand der unten angegebenen Kontextinformationen
        2. Wenn die Informationen im Kontext nicht ausreichen, sage klar: "Diese Information finde ich nicht in den bereitgestellten Paragraphen"
        3. Zitiere IMMER die relevanten Paragraphen (z.B. "gemäß § 433 BGB...")
        4. Sei präzise und verwende die genaue Formulierung aus dem Gesetzestext
        5. Erfinde KEINE Informationen, die nicht im Kontext stehen

        KONTEXT (Relevante BGB-Paragraphen):
        {context}

        FRAGE: {question}

        ANTWORT (mit Paragraphenangaben):"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        rewrite_template = """Formuliere die Nutzerfrage in eine kurze, suchoptimierte Abfrage für eine Vektorsuche über Gesetzestexte. Behalte die Bedeutung bei, entferne Füllwörter und nenne zentrale Rechtsbegriffe. Antworte nur mit der überarbeiteten Abfrage, ohne Erklärungen.

        Nutzerfrage:
        {question}

        Suchabfrage:"""

        self.rewrite_prompt = PromptTemplate(
            template=rewrite_template,
            input_variables=["question"]
        )

        # Create retrieval QA chain
        print("Creating RetrievalQA chain...")
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": self.top_k}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        print("✓ RAG chain initialized successfully")

    def _extract_llm_text(self, result: Any) -> str:
        if isinstance(result, str):
            return result.strip()
        content = getattr(result, "content", None)
        if isinstance(content, str):
            return content.strip()
        return str(result).strip()

    def rewrite_query(self, question: str) -> str:
        if not question:
            return question

        word_count = len(question.split())
        if word_count < self.rewrite_min_words:
            return question

        try:
            prompt = self.rewrite_prompt.format(question=question)
            rewritten = self._extract_llm_text(self.llm.invoke(prompt))
            if rewritten:
                return rewritten
        except Exception as e:
            print(f"Query rewrite failed, using original query: {e}")

        return question

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG chain with a question
        Returns a dictionary with answer and source documents
        """
        if not self.qa_chain:
            self.initialize()

        print(f"\nProcessing query: {question}")

        rewritten_query = self.rewrite_query(question)
        if rewritten_query != question:
            print(f"Rewritten query: {rewritten_query}")

        # Run the chain
        result = self.qa_chain.invoke({"query": rewritten_query})

        # Extract answer and sources
        answer = result.get("result", "")
        source_docs = result.get("source_documents", [])

        # Format sources
        sources = []
        for doc in source_docs:
            section = doc.metadata.get("section", "Unknown")
            title = doc.metadata.get("title", "")
            sources.append({
                "section": section,
                "title": title,
                "content": doc.page_content[:200] + "..."  # Preview
            })

        return {
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources)
        }

    def format_response(self, result: Dict[str, Any]) -> str:
        """Format the query result for display"""
        output = []
        output.append("=" * 80)
        output.append("ANTWORT")
        output.append("=" * 80)
        output.append(result["answer"])
        output.append("\n" + "=" * 80)
        output.append("QUELLEN")
        output.append("=" * 80)

        for i, source in enumerate(result["sources"], 1):
            output.append(f"\n{i}. {source['section']}")
            if source["title"]:
                output.append(f"   {source['title']}")

        output.append("=" * 80)
        return "\n".join(output)


def main():
    """Main function for testing the RAG chain"""
    engine = BGBQueryEngine()
    engine.initialize()

    # Test queries
    test_queries = [
        "Wer erbt, wenn es kein Testament gibt?",
        "Was ist ein Pflichtteil?",
        "Können Enkel erben?"
    ]

    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"Testing query: {query}")
        print('=' * 80)

        try:
            result = engine.query(query)
            print(engine.format_response(result))
        except Exception as e:
            print(f"Error processing query: {e}")


if __name__ == "__main__":
    main()
