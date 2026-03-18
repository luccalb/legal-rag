# BGB Erbrecht RAG - Model Recommendations for German

## Problem Identified
The current setup uses `nomic-embed-text` for embeddings, which performs poorly on German legal language. Retrieval tests show it's fetching completely irrelevant sections.

## Recommended Models

### Embedding Models (Choose ONE):
1. **mxbai-embed-large** (Best for German)
   ```bash
   ollama pull mxbai-embed-large
   ```
   - 334M parameters
   - Excellent multilingual support including German
   - Better semantic understanding

2. **bge-m3** (Alternative)
   ```bash
   ollama pull bge-m3
   ```
   - Multilingual BERT
   - Good for European languages

### LLM Models (Choose ONE):
1. **llama3:8b** (Recommended)
   ```bash
   ollama pull llama3:8b
   ```
   - Better instruction following
   - Good German support
   - 4.7GB

2. **qwen2.5:7b** (Alternative - Good for German)
   ```bash
   ollama pull qwen2.5:7b
   ```
   - Excellent multilingual including German
   - 4.7GB

3. **gemma2:9b** (Alternative)
   ```bash
   ollama pull gemma2:9b
   ```
   - Google's model
   - Decent German support
   - 5.4GB

## Installation Steps

1. Pull the recommended models:
```bash
# Best embedding model for German
ollama pull mxbai-embed-large

# Best LLM for instruction following
ollama pull llama3:8b
```

2. Update `.env` file:
```env
OLLAMA_MODEL=llama3:8b
EMBEDDING_MODEL=mxbai-embed-large
```

3. Rebuild the vector database:
```bash
source venv/bin/activate
rm -rf vector_db
python src/build_vectordb.py
```

4. Test the improved system:
```bash
python main.py "Wer erbt, wenn es kein Testament gibt?"
```

## Expected Improvements
- Retrieval should now find §§ 1924-1931 (legal succession orders)
- LLM should provide accurate German responses
- Citations should be relevant to the question
