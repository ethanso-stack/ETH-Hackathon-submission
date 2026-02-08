# 📊 Earnings Call Analyzer

An AI-powered agent swarm system that analyzes earnings call transcripts and generates comprehensive investment insights using distributed specialist agents.

## 🎯 Overview

This project uses multiple specialized AI agents that collaborate to analyze different aspects of earnings calls:
- **Revenue Agent**: Analyzes top-line growth, guidance, and customer metrics
- **Profitability Agent**: Evaluates margins, costs, and operational efficiency  
- **Management Agent**: Assesses executive tone, confidence, and red flags

The agents communicate through a message bus, challenge each other's findings, and reach consensus on an overall investment verdict.

## ✨ Features

- **Multi-Agent Architecture**: Distributed specialists that debate and validate findings
- **Flexible AI Backend**: Supports Claude API, Ollama (local/free), or demo mode
- **Web Interface**: Clean, modern UI for uploading and analyzing transcripts
- **Real-time Analysis**: Stream results as agents complete their work
- **Comprehensive Scoring**: 0-10 ratings across revenue, profitability, and management
- **Investment Recommendations**: Clear BUY/HOLD/SELL verdicts with confidence levels

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install fastapi uvicorn anthropic ollama pydantic
```

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd earnings-analyzer
```

2. **Choose your AI backend**

**Option A: Claude API (Best Quality)**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
# Get your key from: https://console.anthropic.com
```

**Option B: Ollama (Free & Local)**
```bash
# Install Ollama from https://ollama.com
ollama pull llama3.1
```

**Option C: Demo Mode**
- No setup needed - uses pre-loaded sample analyses

3. **Start the backend**
```bash
python server.py
# Server runs on http://localhost:8001
```

4. **Open the frontend**
```bash
# Simply open index.html in your browser
# Or serve with Python:
python -m http.server 8000
# Then visit http://localhost:8000
```

## 📖 Usage

### Web Interface

1. Open `index.html` in your browser
2. Click "Select File" and upload an earnings transcript (.pdf or .txt)
3. Click "Analyze transcript"
4. View comprehensive analysis with agent scores and consensus verdict

### API Usage

```python
import requests

# Analyze transcript text
response = requests.post(
    "http://localhost:8001/api/analyze",
    json={"text": "Your earnings call transcript here..."}
)

results = response.json()
print(f"Overall Score: {results['consensus']['overall_score']}/10")
print(f"Verdict: {results['consensus']['verdict']}")
```

### CLI Usage

```bash
# Run the analyzer directly
python Earnings_Call_Analyzer.py

# Follow interactive prompts to:
# 1. Choose AI backend (Claude/Ollama/Demo)
# 2. Analyze files or use pre-loaded samples
```

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend (HTML)│
│  - File Upload  │
│  - Visualization│
└────────┬────────┘
         │
         │ HTTP/JSON
         ▼
┌─────────────────┐
│  FastAPI Server │
│  (server.py)    │
└────────┬────────┘
         │
         │ async
         ▼
┌─────────────────────────────────┐
│  Agent Swarm System             │
│  (Earnings_Call_Analyzer.py)    │
│                                  │
│  ┌──────────┐  ┌──────────┐    │
│  │ Revenue  │  │Profit-   │    │
│  │ Agent    │◄─┤ability   │    │
│  └────┬─────┘  │Agent     │    │
│       │        └────┬─────┘    │
│       │  Message    │           │
│       │    Bus      │           │
│       ▼             ▼           │
│  ┌──────────────────────┐      │
│  │  Management Agent    │      │
│  └──────────┬───────────┘      │
│             │                   │
│             ▼                   │
│  ┌──────────────────────┐      │
│  │ Consensus Engine     │      │
│  └──────────────────────┘      │
└─────────────────────────────────┘
         │
         │ Claude API / Ollama
         ▼
┌─────────────────┐
│   AI Models     │
│  - Claude 4     │
│  - Llama 3.1    │
└─────────────────┘
```

## 📁 Project Structure

```
earnings-analyzer/
├── index.html                    # Frontend UI
├── newjavascript.js             # Frontend logic
├── server.py                    # FastAPI backend server
├── Earnings_Call_Analyzer.py   # Core AI agent system
├── api.py                       # API test suite
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Skip interactive prompts (for deployment)
export SKIP_PROMPTS="1"
```

### Customizing Agents

Edit `Earnings_Call_Analyzer.py` to modify:
- Agent weights (default: Revenue 40%, Profitability 35%, Management 25%)
- Scoring thresholds for verdicts
- Prompt templates for each specialist agent

## 🧪 Testing

Run the comprehensive test suite:

```bash
python api.py
```

This tests:
- ✅ Root endpoint
- ✅ Health check
- ✅ Sample retrieval
- ✅ Full AI analysis pipeline
- ✅ Error handling

## 📊 Sample Output

```json
{
  "consensus": {
    "overall_score": 7.8,
    "verdict": "MET EXPECTATIONS - HOLD/BUY",
    "confidence": "High",
    "recommendation": "Solid results but not spectacular...",
    "red_flags": ["None detected"]
  },
  "detailed_analysis": {
    "revenue": {
      "score": 8.2,
      "verdict": "STRONG",
      "highlights": ["Revenue beat estimates by 5.7%", ...]
    },
    "profitability": {
      "score": 6.5,
      "verdict": "MIXED",
      "concerns": ["Margin compression ongoing", ...]
    },
    "management": {
      "score": 7.8,
      "verdict": "CONFIDENT",
      "positive_signals": ["CEO insider buying", ...]
    }
  }
}
```

## 🎓 How It Works

1. **Document Ingestion**: Upload PDF/text transcript
2. **Parallel Analysis**: Three specialist agents analyze simultaneously
3. **Agent Communication**: Agents challenge each other's findings via message bus
4. **Consensus Building**: Weighted scoring produces final verdict
5. **Result Delivery**: Structured JSON with actionable insights

## 🔐 Security Notes

- API keys should never be committed to git
- Use `.gitignore` to exclude sensitive files
- Consider using environment variables for production
- CORS is wide open for development - restrict in production

## 🚀 Deployment

### Production Setup

1. **Backend (Railway/Render/AWS)**
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Frontend (Netlify/Vercel)**
- Deploy `index.html` and `newjavascript.js`
- Update API endpoint in JavaScript to production URL

3. **Environment Variables**
```bash
ANTHROPIC_API_KEY=your-production-key
SKIP_PROMPTS=1
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional specialist agents (competitive analysis, risk assessment)
- Support for more document formats (Word, Excel)
- Historical tracking and trend analysis
- Integration with financial data APIs
- Enhanced visualization of agent debates

## 📝 License

MIT License - feel free to use for personal or commercial projects

## 🙏 Acknowledgments

- Built with Claude 4 and Llama 3.1
- FastAPI for the backend framework
- PDF.js for document parsing
- Anthropic for the AI API

## 📞 Support

For issues or questions:
1. Check the test suite: `python api.py`
2. Review console logs (browser F12 + server terminal)
3. Ensure AI backend is properly configured

---

**Built with ❤️ for financial analysis automation**
