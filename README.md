# BGB Erbrecht RAG

A Retrieval-Augmented Generation (RAG) system for querying German Inheritance Law (BGB Book 5 - Erbrecht) using natural language.

## Features

- **Data Ingestion**: Scrapes BGB Book 5 (Inheritance Law) from official German legal sources
- **Local Vector Store**: Uses ChromaDB for efficient semantic search
- **Local Embeddings**: Uses Ollama with nomic-embed-text for privacy-preserving embeddings
- **Local LLM**: Queries are answered by Mistral or Qwen-2.5-Coder via Ollama
- **Source Citations**: Every answer includes references to specific BGB paragraphs (§)
- **CLI Interface**: Simple command-line interface for queries
- **Web API**: FastAPI endpoint for integration with other applications

## Project Structure

```
legal-rag/
├── data/                    # Scraped BGB data (JSON)
├── vector_db/               # ChromaDB vector store
├── src/                     # Core source code
│   ├── ingest_bgb.py       # BGB scraping logic
│   ├── build_vectordb.py   # Vector database creation
│   └── rag_engine.py       # RAG chain implementation
├── web_api/                 # FastAPI application
│   └── app.py              # API endpoints
├── main.py                 # CLI interface
├── requirements.txt        # Python dependencies
├── .env                    # Configuration settings
└── README.md              # This file
```

## Prerequisites

- Python 3.9 or higher
- [Ollama](https://ollama.ai/) installed and running

## Installation

### 1. Clone and Setup Virtual Environment

```bash
cd legal-rag
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Ollama and Pull Models

Install Ollama from [https://ollama.ai/](https://ollama.ai/)

Then pull the required models:

```bash
# Embedding model
ollama pull nomic-embed-text

# LLM (choose one or both)
ollama pull mistral
ollama pull qwen2.5-coder
```

### 4. Configure Environment

Edit the `.env` file if needed. Default settings:

```env
OLLAMA_MODEL=mistral:latest
EMBEDDING_MODEL=nomic-embed-text
VECTOR_DB_PATH=./vector_db
COLLECTION_NAME=bgb_erbrecht
```

## Setup

### Step 1: Scrape BGB Book 5

```bash
python src/ingest_bgb.py
```

This will:
- Fetch the BGB from gesetze-im-internet.de
- Extract all sections from Book 5 (Erbrecht)
- Save them to `data/bgb_book5.json`

### Step 2: Build Vector Database

```bash
python src/build_vectordb.py
```

This will:
- Load the scraped BGB sections
- Generate embeddings using Ollama
- Store them in ChromaDB at `./vector_db`

**Note**: This may take several minutes depending on your hardware.

## Usage

### Command Line Interface (CLI)

#### Single Query

```bash
python main.py "Wer erbt, wenn es kein Testament gibt?"
```

#### Interactive Mode

```bash
python main.py -i
```

Then type your questions interactively. Type `quit` or `exit` to end the session.

#### Example Queries

```bash
python main.py "Was ist ein Pflichtteil?"
python main.py "Können Enkel erben?"
python main.py "Was passiert mit dem Erbe, wenn alle Erben ausschlagen?"
python main.py "Wie lange ist die Ausschlagungsfrist?"
```

### Web API

Start the FastAPI server:

```bash
cd web_api
python app.py
```

Or using uvicorn directly:

```bash
uvicorn web_api.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

#### Example API Request

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Wer erbt, wenn es kein Testament gibt?", "top_k": 4}'
```

Response format:

```json
{
  "answer": "Wenn es kein Testament gibt, tritt die gesetzliche Erbfolge ein...",
  "sources": [
    {
      "section": "§ 1922",
      "title": "Gesamtrechtsnachfolge",
      "content": "..."
    }
  ],
  "num_sources": 4
}
```

## Configuration

Edit `.env` to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_MODEL` | LLM model name | `mistral:latest` |
| `EMBEDDING_MODEL` | Embedding model | `nomic-embed-text` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `VECTOR_DB_PATH` | ChromaDB storage path | `./vector_db` |
| `COLLECTION_NAME` | ChromaDB collection | `bgb_erbrecht` |
| `CHUNK_SIZE` | Text chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `TOP_K_RESULTS` | Number of sources to retrieve | `4` |

## Troubleshooting

### "RAG engine not initialized"

Make sure you've completed both setup steps:
1. Run `python src/ingest_bgb.py`
2. Run `python src/build_vectordb.py`

### "Connection refused" or Ollama errors

Ensure Ollama is running:

```bash
ollama serve
```

Verify models are installed:

```bash
ollama list
```

### "No sections extracted"

The HTML structure of gesetze-im-internet.de may have changed. Check the `_alternative_parsing` method in `src/ingest_bgb.py` or file an issue.

### Slow performance

- First query is always slower (model loading)
- Consider using a smaller model: `ollama pull mistral:7b`
- Reduce `CHUNK_SIZE` in `.env`
- Reduce `TOP_K_RESULTS` to retrieve fewer sources

## Development

### Testing the RAG Engine

```bash
python src/rag_engine.py
```

This will run a few test queries to verify the RAG chain is working.

### Rebuilding the Vector Database

If you update the scraped data or change embedding settings, rebuild the database:

```bash
rm -rf vector_db/
python src/build_vectordb.py
```

## Technology Stack

- **LangChain**: RAG orchestration and chain management
- **ChromaDB**: Vector database for semantic search
- **Ollama**: Local LLM and embedding model serving
- **BeautifulSoup**: HTML parsing and web scraping
- **FastAPI**: Web API framework
- **Pydantic**: Data validation

## Legal Notice

This project is for educational and research purposes. The BGB text is scraped from the official German government website (gesetze-im-internet.de), which is publicly available. The RAG system provides information based on the BGB but is not a substitute for professional legal advice.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Roadmap

- [ ] Add support for other BGB books
- [ ] Implement conversation history for follow-up questions
- [ ] Add web UI (React/Vue frontend)
- [ ] Support for case law integration
- [ ] Multi-language support (English translations)
- [ ] Fine-tuning specific legal LLM

## Contact

For questions or issues, please open an issue on GitHub.
