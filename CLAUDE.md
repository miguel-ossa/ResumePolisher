# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ResumePolisher is a Gradio-based web application providing AI-powered resume enhancement tools. Uses Llama 3.3 70B Instruct via Hugging Face Inference API.

## Development Commands

**Run the application:**
```bash
python main.py
```
Launches a local server at `http://localhost:7860`.

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## Architecture

### Core Pattern: Shared LLM Client

All four tools share a single `InferenceClient` instance managed via `get_hf_client()`. This reduces API overhead and improves performance. The client is instantiated once and reused across all tabs.

### Component Design

Each tool follows a consistent pattern in `main.py`:
1. `*_tool()` function: Core business logic
2. `_*_tab()` function: Gradio UI component construction
3. Button click handler: Orchestrates function call and error display

The `api_key_state` Gradio State variable is passed to all tabs and serves as the token source.

### Configuration

- `config.py`: Centralized model ID configuration
- `.env`: Environment variables via `python-dotenv`
- `USE_ENV_TOKEN` flag (line 15): Controls whether HF token comes from UI or environment

### Key Functions

**Client Management:**
- `get_hf_client(token=None)`: Returns InferenceClient with appropriate token source

**Tool Implementations:**
- `polish_resume()`: Resume content enhancement for specific roles
- `generate_html()`: Creates downloadable HTML resumes with photo embedding
- `get_career_advice()`: Compares resume to job descriptions
- `generate_cover_letter()`: Generates customized cover letters

**Error Handling:**
- All tool functions return tuple: `(result, error_message)`
- Error messages displayed as HTML blocks using `get_error_html()`
- Exceptions caught and returned as user-friendly error strings

### Prompt Design Considerations

Each tool uses carefully crafted prompts:
- Resume Polisher: Role-specific improvements with optional instruction override
- HTML Generator: Explicit markdown-to-HTML conversion instructions + PHOTO_PLACEHOLDER
- Career Advisor: Focuses on gap identification between job requirements and resume
- Cover Letter: Emphasizes aligning real qualifications with job requirements

### Security

- `.env` contains sensitive tokens (HF_TOKEN)
- `.gitignore` prevents token commits
- API key can be provided via UI (Settings tab) or environment variable
- Base64-encoded photos stored temporarily for HTML generation

## Important Notes

- Single file entry point (`main.py`) - no additional module imports
- All prompts avoid fabricating experience
- HTML generation uses regex cleanup to remove markdown code fences
- Temporary HTML files created via `tempfile.mkstemp()` for downloads