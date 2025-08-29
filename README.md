# ToolLlama 🤖

**The Ultimate AI-Powered Web Assistant & Automation Platform**

Transform your workflow with an intelligent system that combines Ollama's advanced AI capabilities with comprehensive web scraping, data management, and automation tools. Built for researchers, developers, and automation enthusiasts who need powerful AI assistance.

![ToolLlama Dashboard](https://via.placeholder.com/800x400/0f172a/00d4ff?text=ToolLlama+Dashboard)

## ✨ Features

### 🎯 Core Capabilities
- **AI-Powered Chat**: Natural language conversation with Ollama models
- **Advanced Web Scraping**: Multi-engine scraping with AI understanding
- **Smart Data Management**: Organize and analyze collected data
- **Browser Automation**: Automated website interactions and logins
- **Visual Tool Builder**: Drag-and-drop workflow creation
- **Email Integration**: Send emails through AI commands

### 🔧 Technical Features
- **Multi-Model Support**: Llama3, Phi3, Mistral, and more
- **Real-time Collaboration**: Live AI assistance for web tasks
- **Data Export**: JSON, CSV, Excel formats
- **Search & Filter**: Advanced data querying
- **Performance Monitoring**: Usage analytics and optimization
- **Security First**: Encrypted credentials and secure API access

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Ollama** running locally (`ollama serve`)
- **At least one Ollama model** installed (`ollama pull llama3`)

### One-Command Setup
```bash
# Clone and setup everything automatically
python start_system.py
```

This will:
- ✅ Check all dependencies
- ✅ Install missing packages
- ✅ Start backend API server (port 8000)
- ✅ Start frontend dashboard (port 5173)
- ✅ Run system health checks
- ✅ Open browser to dashboard

### Manual Setup (Alternative)

```bash
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt

# 2. Install frontend dependencies
npm install

# 3. Start backend server
python run_backend.py

# 4. Start frontend (in new terminal)
npm run dev

# 5. Open http://localhost:5173
```

## 🎮 How to Use

### 1. **Chat with AI** 💬
- Select your preferred Ollama model
- Ask questions naturally
- Use tools automatically through AI commands

### 2. **Manage Data** 📊
- Create lists for URLs, emails, research notes
- Import/export data in multiple formats
- Search and filter your collections
- Get analytics on your data

### 3. **Automate Web Tasks** 🌐
- Set up browser automation for websites
- Store login credentials securely
- Let AI control browser interactions
- Monitor sessions in real-time

### 4. **Build Custom Tools** 🔧
- Use visual drag-and-drop builder
- Connect tools in workflows
- Test and deploy custom automations
- Share tool configurations

### 5. **Send Emails** 📧
- Connect Gmail or Outlook accounts
- Use AI to compose and send emails
- Schedule email campaigns
- Track delivery status

## 📋 Example Workflows

### Research Assistant
```
1. Use web search to find relevant articles
2. Scrape content from multiple sources
3. Extract key information automatically
4. Store findings in research lists
5. Generate summary reports
```

### Data Collection
```
1. Create URL lists for target websites
2. Set up browser automation for logins
3. Run scraping campaigns
4. Process and clean collected data
5. Export to preferred format
```

### Email Automation
```
1. Connect email account securely
2. Create email templates
3. Use AI to personalize messages
4. Schedule bulk sending
5. Monitor delivery and responses
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI        │
│   Dashboard     │◄──►│   Backend        │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Browser        │    │  Ollama Models  │
│  Automation     │    │  (Llama3, etc)  │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Web Scraping   │    │  Data Storage   │
│  Engines        │    │  & Management   │
└─────────────────┘    └─────────────────┘
```

### Backend Components
- **FastAPI Server**: RESTful API with async support
- **Tool Wrapper**: Ollama tool integration layer
- **Data Manager**: Advanced data storage and retrieval
- **Document Extractor**: Multi-format content extraction
- **Web Search**: Integrated search capabilities

### Frontend Components
- **Chat Interface**: AI conversation with tool calling
- **Data Lists Panel**: Data management and visualization
- **Communication Hub**: Email and messaging tools
- **Browser Control**: Website automation interface
- **Tool Builder**: Visual workflow creation

## 🔧 Configuration

### Environment Variables
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Data Storage
DATA_STORAGE_PATH=/home/user/toollama/data

# Email (Optional)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret

# Security
API_SECRET_KEY=your_secret_key
```

### Model Recommendations
```bash
# General purpose (good balance)
ollama pull llama3

# Code and technical tasks
ollama pull codellama

# Creative and research
ollama pull llama2:13b

# Fast responses
ollama pull phi3
```

## 🧪 Testing

Run comprehensive system tests:
```bash
python test_system.py
```

This will test:
- ✅ Backend API functionality
- ✅ Frontend component loading
- ✅ End-to-end data flows
- ✅ Performance benchmarks
- ✅ Integration scenarios

## 📊 Monitoring

### Health Checks
- **System Health**: `http://localhost:8000/health`
- **API Documentation**: `http://localhost:8000/docs`
- **Frontend Status**: Check browser console

### Analytics
- View usage statistics in Data panel
- Monitor tool performance
- Track data collection metrics
- Analyze AI model effectiveness

## 🔒 Security

### Data Protection
- **Encrypted Credentials**: All stored passwords are encrypted
- **Secure API**: HTTPS recommended for production
- **Input Validation**: All API inputs are validated
- **Rate Limiting**: Built-in request throttling

### Best Practices
- Use strong passwords for email accounts
- Regularly update Ollama models
- Monitor system logs for anomalies
- Backup important data collections

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "run_backend.py"]
```

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB for models and data
- **Network**: Stable internet for web scraping
- **CPU**: Multi-core recommended for concurrent tasks

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python dependencies
pip list | grep fastapi

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

**Frontend not loading:**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Tools not working:**
```bash
# Check backend health
curl http://localhost:8000/health

# Verify tool availability
curl http://localhost:8000/api/tools/scrape_webpage -X POST -d '{"url":"https://httpbin.org/html"}'
```

**Ollama connection issues:**
```bash
# Restart Ollama
ollama serve

# Check model availability
ollama list
```

## 📚 API Reference

### Core Endpoints
```http
GET  /health                    # System health check
POST /api/tools/execute         # Execute any tool
POST /api/tools/scrape_webpage  # Web scraping
POST /api/data/lists           # Create data list
GET  /api/data/lists           # Get all lists
POST /api/communication/send_email # Send email
```

### Tool Schemas
All tools follow this format:
```json
{
  "name": "tool_name",
  "description": "What the tool does",
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {"type": "string", "description": "Parameter description"}
    },
    "required": ["param1"]
  }
}
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Development Setup
```bash
# Backend development
cd backend
pip install -r requirements.txt
python -m pytest tests/

# Frontend development
npm install
npm run build
npm run preview
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for the amazing local AI infrastructure
- **ScrapeGraph-AI** for intelligent web scraping
- **FastAPI** for the robust backend framework
- **React** for the flexible frontend framework

## 📞 Support

- **Documentation**: [Full API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Ready to revolutionize your workflow with AI?** 🚀

Start with `python start_system.py` and explore the power of ToolLlama!