# Resume Polisher

AI-powered suite of interactive tools to help job seekers strengthen their application materials. Built with Python, Gradio, and Llama 3.2 via the Hugging Face Inference API.

## Features

| Tool | What it does |
|------|-------------|
| **Resume Polisher** | Takes your resume and a target position, returns an improved version tailored to that role. Optionally add custom instructions for specific areas of improvement. |
| **Career Advisor** | Compares your resume against a job description and provides targeted advice on what to improve to match the role. |
| **Cover Letter Generator** | Generates a customized cover letter from your resume, company name, position, and job description — highlighting real experience without fabricating qualifications. |

All three tools are available in a single Gradio web app with a tabbed interface.

## Tech Stack

- **LLM:** Meta Llama 3.2 11B Vision Instruct (via Hugging Face Inference API)
- **UI:** Gradio 5.x
- **Config:** `python-dotenv` for environment variables
- **Python:** 3.11+

## Prerequisites

- Python 3.11 or higher
- A Hugging Face account with an API token (sign up at [huggingface.co](https://huggingface.co/))
- Access to the `meta-llama/Llama-3.2-11B-Vision-Instruct` model on Hugging Face

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd ResumePolisher
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your Hugging Face token:
   ```
   HF_TOKEN=your_hugging_face_api_token_here
   ```

## Usage

Launch the unified app with all three tools in one tabbed interface:

```bash
python main.py
```

This starts a local web server (default `http://localhost:7860`). Open the URL shown in your browser to access all tools.

You can also run individual tools directly:

```bash
python resume_polisher.py   # Resume polishing only
python career_advisor.py    # Career advice only
python cover_letter.py      # Cover letter only
```

Each standalone command starts its own Gradio web app on `http://localhost:7860`.

## Project Structure

```
ResumePolisher/
├── main.py              # Unified entry point (3-tab Gradio app)
├── resume_polisher.py   # Standalone resume polishing app
├── career_advisor.py    # Standalone career advice app
├── cover_letter.py      # Standalone cover letter generator
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not tracked)
└── .gitignore
```

`main.py` is the recommended entry point — it launches all three tools in a single app with shared LLM client, reducing API overhead.

## Notes

- The unified `main.py` app shares a single `InferenceClient` across all tabs.
- All prompts are crafted to avoid fabricating experience — the cover letter generator explicitly emphasizes aligning real qualifications with job requirements.
- Each standalone module (`resume_polisher.py`, `career_advisor.py`, `cover_letter.py`) still works independently for focused use.

## License

This project was developed as part of the IBM Generative AI Engineering course on Coursera (Course 6: Building Generative AI-Powered Applications with Python).
