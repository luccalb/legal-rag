# RAG System Issues and Fixes - German Language Support

## Problem Diagnosis

### Issue: Incorrect Answers
When asked "Wer erbt, wenn es kein Testament gibt?" (Who inherits if there's no testament?), the system incorrectly retrieved:
- § 2344 (Unworthiness declaration)
- § 2019 (Immediate replacement)
- § 1949 (Error about calling reason)

**Expected sections**: §§ 1924-1931 (Legal succession orders)

### Root Causes

1. **Embedding Model Issue**: `nomic-embed-text` claims to be multilingual but performs poorly on German legal language
   - Semantic search completely fails to match German queries with relevant paragraphs
   - The embeddings don't capture legal terminology properly

2. **LLM Model**: Mistral works but isn't optimized for German
   - Can produce German text but instruction following could be better

3. **Prompt Template**: Was too vague
   - Didn't emphasize staying within context
   - Didn't provide clear structure for legal responses

4. **Retrieval Parameters**: Only fetching 4 documents
   - For complex legal questions, more context is often needed

## Implemented Fixes

### 1. Updated Configuration (.env)
```diff
- OLLAMA_MODEL=mistral:latest
- EMBEDDING_MODEL=nomic-embed-text
- TOP_K_RESULTS=4

+ OLLAMA_MODEL=llama3:8b
+ EMBEDDING_MODEL=mxbai-embed-large
+ TOP_K_RESULTS=6
```

**Why these models:**
- **mxbai-embed-large**: 334M parameter embedding model with excellent German support
- **llama3:8b**: Better instruction following, strong multilingual including German
- **6 documents**: More context for complex legal questions

### 2. Improved Prompt Template
New prompt includes:
- Explicit rules to only use provided context
- Clear instruction to cite paragraphs
- Warning not to invent information
- Structured format for responses

### 3. Model Alternatives

If `llama3:8b` or `mxbai-embed-large` aren't available, alternatives:

**Embedding Models:**
- `bge-m3`: Good multilingual retrieval
- `intfloat/e5-mistral-7b-instruct` (if available): Larger, better quality

**LLM Models:**
- `qwen2.5:7b`: Excellent German support
- `gemma2:9b`: Google's model, decent German
- `llama3:70b`: Best quality but requires more RAM/VRAM

## Setup Instructions

### Quick Setup (Recommended)
Run the automated setup script:
```bash
./setup_german_models.sh
```

This will:
1. Download mxbai-embed-large and llama3:8b
2. Rebuild vector database with new embeddings
3. Verify setup

### Manual Setup

1. Download models:
```bash
ollama pull mxbai-embed-large
ollama pull llama3:8b
```

2. Update .env (already done):
The file has been updated with the new model names.

3. Rebuild vector database:
```bash
source venv/bin/activate
rm -rf vector_db
python src/build_vectordb.py
```

4. Test:
```bash
python main.py "Wer erbt, wenn es kein Testament gibt?"
```

## Expected Results After Fix

### Query: "Wer erbt, wenn es kein Testament gibt?"

**Should retrieve:**
- § 1924: Gesetzliche Erben erster Ordnung
- § 1925: Gesetzliche Erben zweiter Ordnung
- § 1926: Gesetzliche Erben dritter Ordnung
- § 1931: Gesetzliches Erbrecht des Ehegatten

**Should answer:**
"Wenn kein Testament vorliegt, greift die gesetzliche Erbfolge nach §§ 1924 ff. BGB. Gemäß § 1924 BGB sind gesetzliche Erben erster Ordnung die Abkömmlinge des Erblassers (Kinder, Enkel, etc.). Der überlebende Ehegatte erbt nach § 1931 BGB neben Verwandten der ersten Ordnung zu einem Viertel..."

## Testing

After setup, test with these queries:
```bash
# Test intestate succession
python main.py "Wer erbt, wenn es kein Testament gibt?"

# Test forced share
python main.py "Was ist der Pflichtteil?"

# Test spouse inheritance
python main.py "Wie viel erbt der Ehegatte?"

# Test inheritance orders
python main.py "Was bedeutet Erben erster Ordnung?"
```

## Troubleshooting

### Models not downloading
- Check internet connection
- Ensure Ollama is running: `ollama serve`
- Check disk space (needs ~10GB for both models)

### Still getting bad results
1. Verify models are loaded:
   ```bash
   ollama list
   ```
   Should show: mxbai-embed-large and llama3:8b

2. Ensure vector DB was rebuilt with new embeddings:
   ```bash
   ls -lah vector_db/
   ```
   Check modified timestamp is recent

3. Test retrieval directly:
   ```bash
   python test_queries.py
   ```

### Alternative: Try different model combinations
Edit `.env` and try:
```env
OLLAMA_MODEL=qwen2.5:7b
EMBEDDING_MODEL=bge-m3
```

Then rebuild:
```bash
ollama pull qwen2.5:7b
ollama pull bge-m3
rm -rf vector_db && python src/build_vectordb.py
```

## Performance Notes

- First query after loading models: ~10-30 seconds
- Subsequent queries: ~2-5 seconds
- Database rebuild time: ~3-5 minutes
- Model download time: ~10-15 minutes total

## Cost
- All models run locally
- No API costs
- No data leaves your machine
