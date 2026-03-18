# BGB RAG Web Application

## Lightweight Chat Interface for BGB RAG System

A single-page chat application for querying the German Civil Code (BGB) using natural language.

## Features

✅ **Lightweight Design**
- Vanilla JavaScript (no frameworks)
- Minimal CSS (no UI libraries)
- ~15KB total frontend (HTML + CSS + JS)
- No build process required

✅ **Chat Interface**
- Real-time question/answer flow
- Chat history display
- Auto-scrolling to latest message
- Loading indicators

✅ **BGB Integration**
- Clickable links to source paragraphs
- Automatic conversion: § 1922 → https://www.gesetze-im-internet.de/bgb/__1922.html
- Source citations with titles
- Multiple source display

✅ **User Experience**
- Mobile responsive
- Fast load times
- Simple, clean design
- Error handling

## Quick Start

### 1. Ensure Prerequisites

```bash
# Activate virtual environment
source venv/bin/activate

# Ensure vector database is built
ls -la vector_db/
```

### 2. Start the Server

```bash
# From project root
python web_api/app.py
```

Or with uvicorn:

```bash
uvicorn web_api.app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open Browser

Navigate to: **http://localhost:8000**

## File Structure

```
web_api/
├── app.py                    # FastAPI backend
├── static/
│   ├── index.html           # Single-page chat interface
│   ├── style.css            # Minimal styling (~5KB)
│   └── chat.js              # Vanilla JS logic (~8KB)
└── __init__.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Chat interface (HTML) |
| `/query` | POST | Submit BGB query |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |
| `/api` | GET | API information |

## Usage Examples

### Via Chat Interface

1. Open http://localhost:8000
2. Type your question in German
3. Press "Senden" or Enter
4. View answer with clickable BGB paragraph links

**Example Questions:**
- "Wer erbt, wenn es kein Testament gibt?"
- "Was sind die Pflichten des Verkäufers beim Kaufvertrag?"
- "Was ist Eigentum?"

### Via API

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Wer erbt, wenn es kein Testament gibt?",
    "top_k": 6
  }'
```

Response:
```json
{
  "answer": "Wenn kein Testament vorliegt, greift die gesetzliche Erbfolge...",
  "sources": [
    {
      "section": "§ 1924",
      "title": "Gesetzliche Erben erster Ordnung",
      "content": "..."
    }
  ],
  "num_sources": 6
}
```

## BGB Link Format

The application automatically converts BGB paragraph numbers to official links:

| Section | Generated Link |
|---------|---------------|
| § 1 | https://www.gesetze-im-internet.de/bgb/__1.html |
| § 433 | https://www.gesetze-im-internet.de/bgb/__433.html |
| § 1922 | https://www.gesetze-im-internet.de/bgb/__1922.html |
| § 2385 | https://www.gesetze-im-internet.de/bgb/__2385.html |

## Performance

**Frontend:**
- HTML: ~2KB
- CSS: ~5KB
- JavaScript: ~8KB
- **Total: ~15KB** (uncompressed)
- Load time: <100ms on localhost

**Backend:**
- First query: ~2-5 seconds (model warmup)
- Subsequent queries: ~1-3 seconds
- Memory: Shared with RAG engine

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

## Customization

### Change Styling

Edit `web_api/static/style.css`:
```css
/* Change primary color */
.message.user .message-content {
    background: #27ae60; /* Green instead of blue */
}
```

### Modify Sources Display

Edit `web_api/static/chat.js`:
```javascript
// Change number of sources retrieved
body: JSON.stringify({
    query: query,
    top_k: 10  // Get more sources
})
```

### Add Features

The vanilla JS structure makes it easy to add:
- Export chat history
- Copy answers to clipboard
- Dark mode toggle
- Keyboard shortcuts

## Troubleshooting

### "RAG engine not initialized"

Ensure the vector database is built:
```bash
ls -la vector_db/
# Should show chroma.sqlite3 file

# If missing, rebuild:
python src/build_vectordb.py
```

### Port already in use

Change port in `web_api/app.py`:
```python
uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
```

### Slow responses

- First query is always slower (model loading)
- Check if Ollama is running: `ollama list`
- Reduce `top_k` in chat.js (line with `top_k: 6`)

### Links not working

Verify the section format in the JavaScript console:
- Open Developer Tools (F12)
- Check `sectionToUrl()` function output
- Some special sections (§ 433a) may need manual handling

## Production Deployment

**Security Improvements:**
1. Update CORS settings in `app.py`:
```python
allow_origins=["https://yourdomain.com"]
```

2. Add rate limiting
3. Enable HTTPS
4. Set proper security headers
5. Use reverse proxy (nginx/caddy)

**Performance:**
1. Enable gzip compression
2. Add caching headers
3. Use CDN for static files
4. Consider adding Redis for caching responses

## Development

**Watch Mode:**
```bash
# Auto-reload on file changes
uvicorn web_api.app:app --reload
```

**Debug Mode:**
Open browser console (F12) to see:
- Request/response data
- Error messages
- Loading states

## License

Same as parent project (MIT)
