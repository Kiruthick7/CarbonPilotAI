# CarbonPilot AI - Backend

The backend is a high-performance FastAPI application powered by Python and the Groq API. It handles carbon footprint calculations, scenario simulations, AI-driven chat, and multimodal utility bill parsing.

## Prerequisites
- Python 3.11+
- `uv` (recommended) or standard `pip`
- Groq API Key

## Setup Instructions

### 1. Create a Virtual Environment
We highly recommend using a virtual environment to isolate dependencies.

**Using `uv` (Fastest):**
```bash
# Create the virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

**Using standard `venv`:**
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Environment Variables
Copy the example environment file and add your keys:
```bash
cp .env.example .env
```
Ensure you add your `GROQ_API_KEY` to the `.env` file.

### 3. Run the Development Server
Start the Uvicorn server with hot-reloading:
```bash
uvicorn app.main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`. You can view the interactive OpenAPI documentation at `http://localhost:8000/docs`.

## Project Structure
- `app/api/`: FastAPI route definitions (`/v1/chat`, `/v1/calculate`, etc.)
- `app/models/`: Pydantic models for data validation.
- `app/services/`: Core business logic (CarbonEngine, AgentService).
- `app/agent/`: Groq system prompts and tool definitions.
- `app/data/`: Emission factors and country grid data.
- `app/middleware/`: Rate limiting and security middleware.
