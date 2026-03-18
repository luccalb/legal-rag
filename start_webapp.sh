#!/bin/bash
# Start the BGB RAG Web Application

echo "=========================================="
echo "Starting BGB RAG Web Application"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate || {
        echo "ERROR: Could not activate virtual environment"
        echo "Run: python3 -m venv venv && pip install -r requirements.txt"
        exit 1
    }
fi

# Check if vector database exists
if [ ! -f "vector_db/chroma.sqlite3" ]; then
    echo "WARNING: Vector database not found!"
    echo "Please build it first:"
    echo "  python src/ingest_bgb.py"
    echo "  python src/build_vectordb.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "WARNING: Ollama does not seem to be running"
    echo "Start it with: ollama serve"
    echo ""
fi

echo "Starting FastAPI server..."
echo "==============================================="
echo "  Web UI: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "==============================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python web_api/app.py
