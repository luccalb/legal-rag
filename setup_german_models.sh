#!/bin/bash
# Setup script for improved German language support

echo "=========================================="
echo "BGB Erbrecht RAG - German Model Setup"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Download better German-capable models"
echo "2. Rebuild the vector database with improved embeddings"
echo "3. Test the improved system"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama is not installed!"
    echo "Please install Ollama from https://ollama.ai/"
    exit 1
fi

echo "Step 1: Downloading models (this may take several minutes)..."
echo ""

# Download embedding model
echo "Downloading mxbai-embed-large (multilingual embeddings)..."
ollama pull mxbai-embed-large

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to download mxbai-embed-large"
    exit 1
fi

# Download LLM model
echo ""
echo "Downloading llama3:8b (German-capable LLM)..."
ollama pull llama3:8b

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to download llama3:8b"
    exit 1
fi

echo ""
echo "✓ Models downloaded successfully!"
echo ""

# Activate virtual environment
echo "Step 2: Activating virtual environment..."
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Please run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

# Rebuild vector database
echo ""
echo "Step 3: Rebuilding vector database with new embeddings..."
echo "This will take a few minutes..."
echo ""

rm -rf vector_db
python src/build_vectordb.py

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to rebuild vector database"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ Setup complete!"
echo "========================================"
echo ""
echo "You can now test the improved system:"
echo "  python main.py \"Wer erbt, wenn es kein Testament gibt?\""
echo ""
echo "Or start interactive mode:"
echo "  python main.py -i"
echo ""
