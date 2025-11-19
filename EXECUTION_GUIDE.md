# 🚀 AstraFoundry - Execution Guide

## How to Run the Backend

### Prerequisites

**Required**:
- Python 3.10 or higher
- pip (Python package manager)
- Google API Key (Gemini)

**Optional**:
- Google Search API Key (for enhanced research)
- Google Search Engine ID

---

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd AstraFoundry

# Install required packages
pip install -r requirements.txt
```

**What gets installed**:
- google-generativeai (Gemini API)
- python-dotenv (environment variables)
- pytest (testing)
- Other dependencies

---

## Step 2: Configure Environment

### Create .env file

```bash
# Copy example file
cp .env.example .env
```

### Edit .env file

Open `.env` in your text editor and add your API keys:

```env
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Google Search API (for enhanced research)
GOOGLE_SEARCH_API_KEY=your_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# Optional: Configuration
ENABLE_MEMORY=true
TIMEOUT_SECONDS=300
```

**How to get API keys**:

1. **Gemini API Key** (Required):
   - Go to https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key to your .env file

2. **Google Search API** (Optional):
   - Go to https://console.cloud.google.com/
   - Enable Custom Search API
   - Create credentials
   - Create Custom Search Engine at https://cse.google.com/

---

## Step 3: Run the Pipeline

### Basic Execution

```bash
python src/main.py
```

This will:
1. Prompt you to enter a startup idea
2. Execute all 6 agents sequentially
3. Generate output files in `output/` directory

### With Command-Line Arguments

```bash
# Specify prompt directly
python src/main.py --prompt "Build a climate-tech startup for carbon tracking"

# Specify user ID (for memory personalization)
python src/main.py --prompt "Healthcare AI platform" --user-id john_doe

# Specify output directory
python src/main.py --prompt "FinTech solution" --output my_blueprints/

# Set custom timeout (in seconds)
python src/main.py --prompt "EdTech platform" --timeout 120

# Skip banner
python src/main.py --prompt "AgTech solution" --no-banner
```

### Full Example

```bash
python src/main.py \
  --prompt "Build an AI-powered climate-tech startup for carbon tracking in India" \
  --user-id founder_123 \
  --output blueprints/ \
  --timeout 300 \
  --no-banner
```

---

## Step 4: View Output

### Output Files

The pipeline generates two files in the output directory:

1. **JSON Blueprint** (`blueprint_YYYYMMDD_HHMMSS_<run_id>.json`)
   - Complete structured data
   - All agent outputs
   - Metrics and scores

2. **Text Summary** (`blueprint_YYYYMMDD_HHMMSS_<run_id>_summary.txt`)
   - Human-readable summary
   - Key highlights
   - Next steps

### Example Output Location

```
output/
├── blueprint_20251116_134752_d21290c1.json
└── blueprint_20251116_134752_d21290c1_summary.txt
```

### View Output

```bash
# View JSON (formatted)
cat output/blueprint_*.json | python -m json.tool

# View summary
cat output/blueprint_*_summary.txt

# Open in editor
code output/blueprint_*.json
```

---

## Execution Flow

### What Happens When You Run

```
1. Configuration Validation
   ✓ Check API keys
   ✓ Validate environment

2. Initialize Orchestrator
   ✓ Load agents
   ✓ Initialize tools
   ✓ Setup memory

3. Execute Agent Pipeline
   ⏳ Agent 1/6: Generating startup ideas...
   ⏳ Agent 2/6: Researching market and competitors...
   ⏳ Agent 3/6: Designing product and features...
   ⏳ Agent 4/6: Creating engineering roadmap...
   ⏳ Agent 5/6: Building financial model...
   ⏳ Agent 6/6: Generating pitch deck...

4. Generate Output
   ✓ Save JSON blueprint
   ✓ Save text summary
   ✓ Display results

5. Complete
   🎉 SUCCESS! Your startup blueprint is ready.
```

### Typical Execution Time

- **Idea Agent**: ~5 seconds (API calls)
- **Research Agent**: ~2 seconds (API calls)
- **Product Agent**: <1 second (fast computation)
- **Roadmap Agent**: <1 second (fast computation)
- **Finance Agent**: <1 second (fast computation)
- **Pitch Agent**: <1 second (fast computation)

**Total**: ~7-10 seconds

---

## Troubleshooting

### Common Issues

#### 1. "GOOGLE_API_KEY not found"

**Problem**: API key not set in .env file

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Edit .env and add key
nano .env
# or
code .env
```

#### 2. "Module not found"

**Problem**: Dependencies not installed

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep google-generativeai
```

#### 3. "Permission denied"

**Problem**: Python not executable or wrong permissions

**Solution**:
```bash
# Make main.py executable
chmod +x src/main.py

# Or use python explicitly
python src/main.py
```

#### 4. "API quota exceeded"

**Problem**: Too many API calls

**Solution**:
- Wait a few minutes
- Check API quota in Google Cloud Console
- Use a different API key

#### 5. "Timeout error"

**Problem**: Pipeline taking too long

**Solution**:
```bash
# Increase timeout
python src/main.py --prompt "Your idea" --timeout 600
```

#### 6. Unicode encoding error (Windows)

**Problem**: Console can't display emojis

**Solution**:
```bash
# Set encoding
set PYTHONIOENCODING=utf-8
python src/main.py --prompt "Your idea"

# Or use --no-banner flag
python src/main.py --prompt "Your idea" --no-banner
```

---

## Advanced Usage

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term
```

### Running Individual Agents

You can test individual agents:

```python
# test_single_agent.py
from src.agents.idea_agent import IdeaAgent
from src.tools.google_search_adapter import GoogleSearchAdapter

# Initialize
search_tool = GoogleSearchAdapter(api_key="your_key", engine_id="your_id")
agent = IdeaAgent(search_tool)

# Create context
context = {
    'user_prompt': 'Build a climate-tech startup',
    'user_id': 'test_user',
    'run_id': 'test_123'
}

# Execute
output = agent.execute(context)
print(output.data)
```

### Using Docker

```bash
# Build image
docker build -t astrafoundry .

# Run container
docker run -e GOOGLE_API_KEY=your_key astrafoundry \
  --prompt "Your startup idea"
```

### Environment Variables

All available environment variables:

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional - Google Search
GOOGLE_SEARCH_API_KEY=your_search_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id

# Optional - Configuration
ENABLE_MEMORY=true              # Enable memory bank
TIMEOUT_SECONDS=300             # Pipeline timeout
LOG_LEVEL=INFO                  # Logging level
OUTPUT_DIR=output               # Output directory

# Optional - MCP Tools
MCP_ENABLED=false               # Enable MCP tools
```

---

## Example Sessions

### Session 1: Climate Tech

```bash
$ python src/main.py --prompt "Build a climate-tech startup for carbon tracking"

⏳ Validating configuration...
✅ Configuration validated

🎯 Generating blueprint for: 'Build a climate-tech startup for carbon tracking'
👤 User ID: default_user

======================================================================
🚀 EXECUTING MULTI-AGENT PIPELINE
======================================================================

⏳ Agent 1/6: Generating startup ideas...
⏳ Agent 2/6: Researching market and competitors...
⏳ Agent 3/6: Designing product and features...
⏳ Agent 4/6: Creating engineering roadmap...
⏳ Agent 5/6: Building financial model...
⏳ Agent 6/6: Generating pitch deck...
✅ Pipeline execution complete!

======================================================================
📊 BLUEPRINT RESULTS
======================================================================

💡 Startup Idea: Climate-Tech Marketplace
   Two-sided marketplace connecting climate-tech providers with customers

📈 Market Size: $3.2B USD
   Growth Rate: 18% CAGR

💰 Year 1 Revenue: $600,000
   Runway: 2 months

⚡ Execution Time: 7.2 seconds
   Status: SUCCESS

⏳ Saving blueprint files...
✅ JSON saved to: output/blueprint_20251116_134752_d21290c1.json
✅ Summary saved to: output/blueprint_20251116_134752_d21290c1_summary.txt

======================================================================
🎉 SUCCESS! Your startup blueprint is ready.
======================================================================
```

### Session 2: Healthcare AI

```bash
$ python src/main.py --prompt "Healthcare AI platform for patient monitoring" --user-id doctor_jane

# Similar output with healthcare-specific results
```

---

## Performance Optimization

### Tips for Faster Execution

1. **Use local cache**: Results are cached in memory during session
2. **Reduce timeout**: Set lower timeout for faster failure detection
3. **Skip optional tools**: Disable MCP tools if not needed
4. **Batch processing**: Process multiple ideas in sequence

### Monitoring Performance

```bash
# Check execution time
time python src/main.py --prompt "Your idea"

# View detailed metrics
cat output/blueprint_*.json | jq '.metrics'
```

---

## Production Deployment

### Local Server

```bash
# Run as background service
nohup python src/main.py --prompt "Your idea" > output.log 2>&1 &
```

### Docker Deployment

```bash
# Build and run
docker build -t astrafoundry .
docker run -d -e GOOGLE_API_KEY=your_key astrafoundry
```

### Cloud Deployment

See `PRODUCTION_READINESS.md` for:
- Vertex AI Agent Engine deployment
- Cloud Run deployment
- Kubernetes deployment

---

## Getting Help

### Check Logs

```bash
# View recent logs
tail -f output.log

# Search for errors
grep ERROR output.log
```

### Debug Mode

```bash
# Set debug logging
export LOG_LEVEL=DEBUG
python src/main.py --prompt "Your idea"
```

### Community Support

- GitHub Issues: [Your GitHub URL]/issues
- Kaggle Discussion: [Competition URL]
- Documentation: All .md files in repository

---

## Quick Reference

### Common Commands

```bash
# Basic run
python src/main.py

# With prompt
python src/main.py --prompt "Your idea"

# Run tests
pytest tests/ -v

# Check version
python --version

# List dependencies
pip list

# Update dependencies
pip install -r requirements.txt --upgrade
```

### File Locations

- **Source Code**: `src/`
- **Tests**: `tests/`
- **Output**: `output/`
- **Config**: `.env`
- **Logs**: Console output

---

## Next Steps

After successful execution:

1. **Review Output**: Check JSON and summary files
2. **Analyze Results**: Review market data, features, financials
3. **Iterate**: Run with different prompts
4. **Deploy**: Follow production deployment guide
5. **Share**: Submit to Kaggle competition

---

**You're ready to run AstraFoundry!** 🚀

Start with a simple prompt and explore the generated blueprints. Each run takes ~7 seconds and produces a complete startup plan.

Happy building! 🎉
