# ToolLlama Backend API

Advanced FastAPI backend for Ollama tool integration with comprehensive web scraping and data management capabilities.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the backend:**
   ```bash
   python run_backend.py
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## 📋 API Endpoints

### Core Tools
- `POST /api/tools/scrape_webpage` - Scrape any webpage
- `POST /api/tools/scrape_auction_data` - Scrape government auction sites
- `POST /api/tools/extract_text` - Extract text from URLs
- `POST /api/tools/extract_tables` - Extract tables from URLs
- `POST /api/tools/extract_links` - Extract links from URLs
- `POST /api/tools/extract_images` - Extract images from URLs
- `POST /api/tools/web_search` - Perform web searches

### Data Management
- `POST /api/data/lists` - Create data lists
- `POST /api/data/lists/items` - Add items to lists
- `GET /api/data/lists` - Get all lists
- `GET /api/data/lists/{id}` - Get specific list
- `POST /api/data/lists/{id}/export` - Export list data
- `GET /api/data/search` - Search across lists
- `GET /api/data/lists/{id}/stats` - Get list statistics
- `GET /api/data/analytics` - Get system analytics

### Communication
- `POST /api/communication/send_email` - Send emails

### System
- `GET /health` - Health check
- `GET /` - API info

## 🛠️ Tool Integration

### Ollama Tool Schema Example

```json
{
  "name": "scrape_webpage",
  "description": "Scrape any webpage using AI-powered extraction",
  "parameters": {
    "type": "object",
    "properties": {
      "url": {"type": "string", "description": "URL to scrape"},
      "extraction_prompt": {"type": "string", "description": "What data to extract"},
      "method": {"type": "string", "enum": ["auto", "scrapegraph", "crawl4ai", "browser-use", "playwright"]}
    },
    "required": ["url"]
  }
}
```

### Frontend Integration

```javascript
// Example: Call scraping tool
const response = await fetch('/api/tools/scrape_webpage', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://example.com',
    extraction_prompt: 'Extract main content and links',
    method: 'auto'
  })
});
```

## 📊 Data Management

### List Types
- **urls** - Web URLs and links
- **emails** - Email addresses
- **phones** - Phone numbers
- **research** - Research notes and findings
- **general** - Mixed data types

### Export Formats
- **json** - Structured JSON data
- **csv** - Comma-separated values
- **excel** - Excel spreadsheet (.xlsx)

### Search & Filtering
- Full-text search across all lists
- Filter by list type and tags
- Date range filtering
- Source-based filtering

## 🔧 Configuration

### Environment Variables
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434

# Data Storage
DATA_STORAGE_PATH=/home/scrapedat/toollama/data

# Email Configuration (future)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
```

### Dependencies Status
The API automatically detects available tools:
- ✅ **AI Scrapers**: ScrapeGraph-AI, Crawl4AI, Browser-Use, Playwright
- ✅ **Document Extraction**: PDF, image OCR, web content
- ✅ **Web Search**: DuckDuckGo integration
- ✅ **Data Management**: Enhanced storage with analytics
- 🚧 **Email Integration**: Gmail OAuth (planned)

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_backend.py
```

Tests cover:
- Health checks
- Data list operations
- Web scraping
- Document extraction
- Web search
- Error handling

## 📈 Monitoring

### Health Endpoints
- `/health` - Service availability and status
- `/api/data/analytics` - Usage statistics and metrics

### Logs
All operations are logged with timestamps and can be monitored for:
- Tool execution success/failure
- Performance metrics
- Error patterns
- Usage analytics

## 🔒 Security

- CORS configured for React development
- Input validation on all endpoints
- Error handling without information leakage
- Rate limiting considerations (future enhancement)

## 🚀 Production Deployment

For production use:
1. Configure proper CORS origins
2. Set up reverse proxy (nginx/Caddy)
3. Enable SSL/TLS
4. Configure monitoring and logging
5. Set up backup strategies for data

## 📝 API Versioning

- Current: v1.0.0
- All endpoints are prefixed with `/api/`
- Breaking changes will increment major version

## 🆘 Troubleshooting

### Common Issues

1. **"AI scrapers not available"**
   - Install auction intelligence dependencies
   - Run: `python /home/scrapedat/projects/auction_intelligence/install_ai_scrapers.py`

2. **"Custom tools not available"**
   - Ensure all Python dependencies are installed
   - Check import paths in main.py

3. **Connection errors**
   - Verify Ollama is running on port 11434
   - Check network connectivity

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Test all changes with `test_backend.py`
2. Update documentation for new endpoints
3. Follow existing code patterns
4. Add appropriate error handling