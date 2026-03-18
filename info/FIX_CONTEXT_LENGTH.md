# Fix for "Input Length Exceeds Context Length" Error

## Problem
When building the vector database, you encountered:
```
✗ Error building vector database: Error raised by inference API HTTP code: 500,
{"error":"the input length exceeds the context length"}
```

## Root Cause
Embedding models have a **maximum context length** (token limit) they can process:
- Most embedding models: ~512 tokens max
- Some BGB sections are very long (e.g., § 2033 has multiple long paragraphs)
- Without chunking, long sections exceed the model's capacity

## Solution Implemented

### 1. **Enabled Intelligent Chunking** (src/build_vectordb.py)

The `chunk_documents()` method now:
- Estimates token count for each document (1 token ≈ 4 chars for German)
- Only chunks documents exceeding 400 tokens (~1600 chars)
- Leaves shorter sections intact for better retrieval
- Preserves all metadata (section number, title) in chunks

**Key Logic:**
```python
estimated_tokens = len(doc.page_content) / 4
if estimated_tokens > 400:  # Leave 100 token safety margin
    chunks = text_splitter.split_documents([doc])
    # Preserve metadata in all chunks
```

### 2. **Updated Chunk Size Settings** (.env)
```env
CHUNK_SIZE=1600     # ~400 tokens (fitting within 512 token limit)
CHUNK_OVERLAP=200   # Maintain context between chunks
```

**Why 1600 characters?**
- Embedding models typically support ~512 tokens
- German: 1 token ≈ 4 characters
- 512 tokens × 4 = 2048 chars
- Use 1600 to leave safety margin for tokenization variations

### 3. **Better Separators**
Added period-space (". ") as separator to split at sentence boundaries:
```python
separators=["\n\n", "\n", ". ", " ", ""]
```

This ensures chunks break at natural points in legal text.

## What Happens Now

### Before (Failed):
```
§ 2033: [5000 characters of text]
→ Try to embed → ERROR: Too long!
```

### After (Success):
```
§ 2033: [5000 characters]
→ Split into 4 chunks:
   - Chunk 0: [1600 chars] ✓
   - Chunk 1: [1600 chars] ✓
   - Chunk 2: [1600 chars] ✓
   - Chunk 3: [1200 chars] ✓
→ All chunks successfully embedded
→ Each chunk retains: section=§ 2033, title, chunk_index
```

### Short Sections (Not Chunked):
```
§ 1922: [400 characters]
→ Under 1600 chars → Keep intact ✓
→ Better retrieval for short sections
```

## Rebuild Database

Now you can rebuild without errors:
```bash
source venv/bin/activate
rm -rf vector_db
python src/build_vectordb.py
```

Expected output:
```
Created 451 documents
Split 451 documents into ~520 chunks  # Only long sections split
✓ Vector store created with ~520 documents
```

## Model Compatibility

This chunking strategy works with:
- ✅ `nomic-embed-text-v2-moe` (current)
- ✅ `mxbai-embed-large` (recommended)
- ✅ `bge-m3`
- ✅ Most other embedding models with 512+ token limits

## Benefits of This Approach

1. **No More Errors**: All documents fit within model limits
2. **Smart Chunking**: Only chunks long sections, preserves short ones
3. **Better Retrieval**: Can match specific parts of long sections
4. **Metadata Preserved**: Each chunk knows its source § and position
5. **Future-Proof**: Works with various embedding models

## Verification

After rebuilding, test that retrieval works:
```bash
# Test short section retrieval
python test_queries.py

# Test full RAG
python main.py "Wer erbt, wenn es kein Testament gibt?"
```

You should now see relevant § 1924-1931 sections retrieved correctly.
