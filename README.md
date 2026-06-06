# Resume Polisher

AI-powered suite of interactive tools to help job seekers strengthen their application materials. Built with Python, Gradio, and Llama 3.3 via the Hugging Face Inference API.

## Project Goals

This is an AI-powered suite of interactive tools designed to help job seekers strengthen their application materials. The project provides four distinct but complementary tools for resume enhancement and job application preparation:

1. Resume Polisher - Takes a resume and target position, returning an improved version tailored to that role
2. HTML Resume Generator - Creates professional HTML versions of resumes that can be easily shared or embedded
3. Cover Letter Generator - Generates customized cover letters from resume content, company name, position, and job description
4. Career Advisor - Compares a resume against a job description and provides targeted advice on improvements
5. Settings - Allows entering your own Hugging Face API Key

## Tech Stack

- **LLM:** Meta Llama 3.3 70B Instruct (via Hugging Face Inference API)
- **UI:** Gradio 5.x (with version 6.16.0 in requirements)
- **Config:** `python-dotenv` for environment variables
- **Python:** 3.11+

## Implementation Approach

The application uses a unified Gradio interface with four tabs, each representing one of the core tools. The key architectural decisions include:

1. Shared LLM Client: All tools share a single InferenceClient instance to reduce API overhead and improve efficiency
2. Modular Design: Each tool is implemented as a separate function with its own tab structure, making the code organized and maintainable
3. Prompt Engineering: Each tool uses carefully crafted prompts optimized for its specific task:
  - Resume polishing focuses on role-specific improvements
  - HTML generation includes detailed markdown-to-HTML conversion instructions
  - Career advice compares job requirements with resume content
  - Cover letter generation emphasizes alignment with actual resume experience

## Key Features and Technical Details

1. HTML Generation with Image Support:
  - Supports profile photo upload and embedding in generated HTML
  - Converts markdown syntax to proper HTML tags (bold, italic, code, tables, lists)
  - Uses responsive design with inline CSS for maximum compatibility
  - Handles fallback scenarios when placeholders are missing

2. Shared LLM Client:
  - Single InferenceClient instance shared across all tabs
  - Uses meta-llama/Llama-3.3-70B-Instruct model for all operations
  - Configured with appropriate temperature and token settings for each task type

3. Error Handling
  - Input sanitization is handled through the LLM's own processing (the prompts are carefully crafted)
  - The application follows standard Python project structure with proper separation of concerns

This is a well-designed, production-ready application that leverages modern AI capabilities to provide practical value to job seekers while demonstrating good software engineering practices in its implementation.

## Project Structure

```
ResumePolisher/
├── main.py              # Unified entry point (4-tab Gradio app)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not tracked)
└── .gitignore           # Git ignore rules
```

The main.py file serves as the single entry point that orchestrates all four tools while sharing a single LLM client, which is an optimization to reduce API call overhead and improve performance.

## Security and Best Practices

- Environment variables are properly managed via python-dotenv
- The .gitignore file ensures sensitive information like API tokens aren't committed
- Input sanitization is handled through the LLM's own processing (the prompts are carefully crafted)
- The application follows standard Python project structure with proper separation of concerns

This is a well-designed, production-ready application that leverages modern AI capabilities to provide practical value to job seekers while demonstrating good software engineering practices in its implementation.

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

Launch the unified app with all four tools in one tabbed interface:

```bash
python main.py
```

This starts a local web server (default `http://localhost:7860`). Open the URL shown in your browser to access all tools.

## Hugging Face Token

The application now supports providing your own Hugging Face token at execution time through the UI. This feature allows you to use your personal API token instead of relying on a default token, enabling better control over your usage and avoiding potential rate limiting issues.

## Notes

- The unified `main.py` app shares a single `InferenceClient` across all tabs.
- All prompts are crafted to avoid fabricating experience — the cover letter generator explicitly emphasizes aligning real qualifications with job requirements.

## License

This project was developed (and extended and personalized to work locally) as part of the IBM Generative AI Engineering course on Coursera (Course 6: Building Generative AI-Powered Applications with Python).
