# Resume Polisher

AI-powered suite of interactive tools to help job seekers strengthen their application materials. Built with Python, Gradio, and Llama 3.2 via the Hugging Face Inference API.

## Features

| Tool | What it does |
|------|-------------|
| **Resume Polisher** (`resume_polisher.py`) | Takes your resume and a target position, returns an improved version tailored to that role. Optionally accept custom instructions for specific areas of improvement. |
| **Career Advisor** (`career_advisor.py`) | Compares your resume against a job description and provides targeted advice on what to improve to match the role. |
| **Cover Letter Generator** (`cover_letter.py`) | Generates a customized cover letter from your resume, the company name, position, and job description — highlighting real experience without fabricating qualifications. |

Each tool runs as an independent Gradio web app with a clean browser-based UI.

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

Run any tool individually — each launches its own Gradio UI:

```bash
# Polish your resume for a specific role
python resume_polisher.py

# Get targeted career advice based on a job description
python career_advisor.py

# Generate a customized cover letter
python cover_letter.py
   ```

Each command starts a local web server (default `http://localhost:7860`). Open the URL shown in your browser to use the app.

## Project Structure

```
ResumePolisher/
├── resume_polisher.py   # Resume polishing Gradio app
├── career_advisor.py    # Career advice Gradio app
├── cover_letter.py      # Cover letter generator Gradio app
├── main.py              # Entry point (placeholder)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not tracked)
└── .gitignore
```

## Notes

- Each app is self-contained and runs independently.
- The `main.py` file is currently a placeholder and not yet wired to the tools.
- All prompts are crafted to avoid fabricating experience — the cover letter generator explicitly emphasizes aligning real qualifications with job requirements.

## License

This project was developed as part of the IBM Generative AI Engineering course on Coursera (Course 6: Building Generative AI-Powered Applications with Python).
