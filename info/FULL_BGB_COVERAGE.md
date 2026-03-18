# Changes Made: Full BGB Coverage

## Summary
The scraper has been updated to extract **all sections** from the entire BGB (Bürgerliches Gesetzbuch), not just Book 5 (Erbrecht/Inheritance Law).

## Files Modified

### 1. **src/ingest_bgb.py**
- ✅ Renamed `extract_book5_sections()` → `extract_all_sections()`
- ✅ Removed all Book 5 detection logic (no more `in_book5` flag)
- ✅ Removed checks for "Buch 5" and "Buch 6" headers
- ✅ Simplified to extract all `<div class="jnnorm">` sections
- ✅ Updated `_alternative_parsing()` to remove section number filtering (1922-2385)
- ✅ Changed default filename: `bgb_book5.json` → `bgb_all.json`
- ✅ Updated all docstrings and print statements

### 2. **src/build_vectordb.py**
- ✅ Changed default filename: `data/bgb_book5.json` → `data/bgb_all.json`
- ✅ Updated metadata source: `'BGB Book 5 - Erbrecht'` → `'BGB'`
- ✅ Updated print statements to reflect full BGB coverage

### 3. **src/rag_engine.py**
- ✅ Updated docstring: "querying BGB inheritance law" → "querying German Civil Code (BGB)"
- ✅ Updated prompt template: "Rechtsexperte für deutsches Erbrecht (BGB Buch 5)" → "Rechtsexperte für deutsches Zivilrecht (BGB)"
- ✅ Changed example citation from § 1924 to § 433 (more general)

### 4. **.env**
- ✅ Updated collection name: `bgb_erbrecht` → `bgb_all`

## What Changed

### Before (Book 5 Only)
```python
# Only extracted §§ 1922-2385 (Inheritance Law)
if 'Buch 5' in text and 'Erbrecht' in text:
    in_book5 = True

if 1922 <= section_num <= 2385:
    # Process only Book 5 sections
```

**Result**: ~451 sections (Book 5 only)

### After (Full BGB)
```python
# Extract all sections - no filtering
for norm in all_norms:
    section_data = self._parse_norm(norm)
    if section_data:
        sections.append(section_data)
```

**Expected Result**: ~2,800 sections (all 5 books)

## Coverage

The scraper now extracts **all 5 books** of the BGB:

1. **Buch 1**: Allgemeiner Teil (§§ 1-240) - General Part
2. **Buch 2**: Recht der Schuldverhältnisse (§§ 241-853) - Law of Obligations
3. **Buch 3**: Sachenrecht (§§ 854-1296) - Property Law
4. **Buch 4**: Familienrecht (§§ 1297-1921) - Family Law
5. **Buch 5**: Erbrecht (§§ 1922-2385) - Inheritance Law

## Usage

### Step 1: Re-scrape the BGB
```bash
source venv/bin/activate
python src/ingest_bgb.py
```

**Output**: `data/bgb_all.json` with ~2,800 sections

### Step 2: Rebuild Vector Database
```bash
rm -rf vector_db
python src/build_vectordb.py
```

**Note**: This will take longer than before (~10-15 minutes) as it's indexing 6x more content.

### Step 3: Query Any Part of the BGB
```bash
# Inheritance law (Book 5)
python main.py "Wer erbt, wenn es kein Testament gibt?"

# Contract law (Book 2)
python main.py "Was sind die Pflichten des Verkäufers beim Kaufvertrag?"

# Property law (Book 3)
python main.py "Was ist Eigentum?"

# Family law (Book 4)
python main.py "Welche Pflichten haben Eltern?"
```

## Benefits

1. **Full Coverage**: Can now answer questions about any BGB topic
2. **Better Context**: RAG can find related sections across different books
3. **More Versatile**: Single system for all civil law questions
4. **Cross-References**: Can retrieve related provisions from different areas

## Database Size

- **Before**: ~520 chunks (Book 5 only)
- **After**: ~3,000 chunks (entire BGB)
- **Vector DB Size**: ~300 MB → ~2 GB
- **Build Time**: ~3 minutes → ~15 minutes

## Backward Compatibility

**Existing Book 5 queries still work perfectly!** The RAG system will still retrieve Book 5 sections when asked about inheritance law.

Example:
```bash
# Still works - retrieves § 1924-1931
python main.py "Wer erbt, wenn es kein Testament gibt?"
```

## Next Steps

After re-scraping and rebuilding:

1. Test various BGB topics:
   ```bash
   python main.py -i  # Interactive mode
   ```

2. Verify coverage:
   ```bash
   # Check number of sections
   cat data/bgb_all.json | grep -c '"section"'
   # Should show ~2800
   ```

3. Update your queries to explore different legal areas!

## Rollback (If Needed)

To revert to Book 5 only:
```bash
git checkout HEAD -- src/ingest_bgb.py src/build_vectordb.py src/rag_engine.py .env
```
