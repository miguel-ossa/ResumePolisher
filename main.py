"""Unified entry point for the Resume Polisher suite.

Launches a single Gradio app with four tabs:
  - Resume Polisher
  - Career Advisor
  - Cover Letter Generator
  - HTML Resume

Each tab reuses the logic from its respective module while sharing
a single Hugging Face InferenceClient instance.

Usage:
    python main.py
"""

import os
import re
import base64
import tempfile
from huggingface_hub import InferenceClient
import gradio as gr
from dotenv import load_dotenv

load_dotenv(override=True)
hf_token = os.getenv("HF_TOKEN")

# Shared model and client
MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct"
client = InferenceClient(token=hf_token)


# --------------------------------------------------------------------------- #
#  Resume Polisher                                                            #
# --------------------------------------------------------------------------- #
def polish_resume(position_name, resume_content, polish_prompt):
    if polish_prompt and polish_prompt.strip():
        prompt = (
            f"Given the resume content: '{resume_content}', polish it based on "
            f"the following instructions: {polish_prompt} for the {position_name} position."
        )
    else:
        prompt = (
            f"Suggest improvements for the following resume content: '{resume_content}' "
            f"to better align with the requirements and expectations of a {position_name} "
            f"position. Return the polished version, highlighting necessary adjustments for "
            f"clarity, relevance, and impact in relation to the targeted role."
        )

    response = client.chat_completion(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=2048,
    )
    return response.choices[0].message.content


def _resume_polisher_tab():
    with gr.Row():
        position = gr.Textbox(label="Position Name", placeholder="Enter the name of the position...")
    with gr.Row():
        resume = gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=15)
    with gr.Row():
        instructions = gr.Textbox(label="Polish Instructions (Optional)", placeholder="Enter specific areas for improvement...", lines=2)
    output = gr.Textbox(label="Polished Resume")
    btn = gr.Button("Polish Resume", variant="primary")
    btn.click(fn=polish_resume, inputs=[position, resume, instructions], outputs=output)

# --------------------------------------------------------------------------- #
#  Html Generation                                                            #
# --------------------------------------------------------------------------- #
def generate_html(photo, resume):
    print("=== generate_html started ===")

    # Convert photo to base64
    photo_html = ""
    if photo:
        try:
            with open(photo, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode("utf-8")
                if photo.lower().endswith(('.png')):
                    mime = "image/png"
                elif photo.lower().endswith(('.jpg', '.jpeg')):
                    mime = "image/jpeg"
                else:
                    mime = "image/png"
                photo_data_url = f"data:{mime};base64,{img_data}"
                photo_html = f'<img src="{photo_data_url}" alt="Profile Photo" style="width: 130px; height: 130px; border-radius: 50%; object-fit: cover; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
                print("Photo converted to base64")
        except Exception as e:
            print(f"Error: {e}")

    # Prompt with placeholder and markdown-to-HTML instruction
    prompt = f"""
You are an expert HTML/CSS developer. Generate a clean, professional HTML resume.

**CRITICAL – MARKDOWN CONVERSION**:
- The resume content may contain markdown syntax (e.g., **bold**, *italic*, `code`, tables, lists).
- You MUST convert all markdown into proper HTML tags: <strong> for **bold**, <em> for *italic*, <code> for `code`, <table> for markdown tables, <ul>/<li> for lists, etc.
- Do NOT output raw markdown characters like **, *, |, ---, etc.

**LAYOUT**:
- In the header section, place the exact text `{{{{PHOTO_PLACEHOLDER}}}}` where the profile photo should appear.
- Use flexbox or grid so that the image sits on the left and the name/title/contact text on the right, aligned vertically.
- Do NOT write "Profile Photo" as text.

**Other requirements**:
1. Modern HTML5, inline CSS, responsive (max-width 900px, centered).
2. No external files or scripts.
3. Preserve all sections from the resume.
4. Return ONLY raw HTML starting with <!DOCTYPE html>. No markdown code fences.

Resume content:
{resume}

Now generate the HTML.
"""
    print("Calling LLM...")
    response = client.chat_completion(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4096,
    )
    html = response.choices[0].message.content
    # Remove markdown code fences
    html = re.sub(r"^```html?\s*", "", html, flags=re.MULTILINE)
    html = re.sub(r"\s*```\s*$", "", html, flags=re.MULTILINE)

    # -------------------------------------------------------------------
    # POST-PROCESS: catch any leftover markdown patterns
    # -------------------------------------------------------------------
    # Convert **bold** to <strong>
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # Convert *italic* to <em> (but not inside existing tags)
    html = re.sub(r'(?<![> ])\*(.+?)\*(?![< ])', r'<em>\1</em>', html)
    # Convert `code` to <code>
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    # Convert markdown links [text](url) to <a>
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Replace placeholder with actual image HTML
    if photo_html:
        if "{{PHOTO_PLACEHOLDER}}" in html:
            html = html.replace("{{PHOTO_PLACEHOLDER}}", photo_html)
            print("Placeholder replaced")
        else:
            # Fallback: inject floated image after <body>
            print("Placeholder missing – injecting floated image")
            body_match = re.search(r"<body[^>]*>", html, re.IGNORECASE)
            if body_match:
                pos = body_match.end()
                inject = f'<div style="float: left; margin: 0 25px 15px 0;">{photo_html}</div><div style="clear: both;"></div>'
                html = html[:pos] + inject + html[pos:]
            else:
                html = f'<div style="float: left; margin-right: 20px;">{photo_html}</div>' + html

    # Remove any leftover "Profile Photo" text
    html = re.sub(r'(?i)Profile Photo', '', html)

    # Save HTML
    fd, path = tempfile.mkstemp(suffix=".html", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML saved at: {path}")

    return gr.update(visible=True, value=path)

def _generate_html_tab():
    with gr.Row():
        photo = gr.Image(label="Profile Photo", type="filepath", height=200)
    with gr.Row():
        resume = gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=15)
    output = gr.File(label="Download HTML Resume")   # No visible=False – always visible but empty until generation
    btn = gr.Button("Generate HTML", variant="primary")
    btn.click(fn=generate_html, inputs=[photo, resume], outputs=output)

# --------------------------------------------------------------------------- #
#  Career Advisor                                                             #
# --------------------------------------------------------------------------- #
def get_career_advice(position, job_desc, resume_content):
    prompt = (
        f"Considering the job description: {job_desc}, and the resume provided: "
        f"{resume_content}, identify areas for enhancement in the resume. Offer specific "
        f"suggestions on how to improve these aspects to better match the job requirements "
        f"and increase the likelihood of being selected for the position of {position}."
    )

    response = client.chat_completion(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=1024,
    )
    return response.choices[0].message.content

def _career_advisor_tab():
    with gr.Row():
        position = gr.Textbox(label="Position Applied For", placeholder="Enter the position you are applying for...")
    with gr.Row():
        job_desc = gr.Textbox(label="Job Description", placeholder="Paste the job description here...", lines=10)
    with gr.Row():
        resume = gr.Textbox(label="Your Resume Content", placeholder="Paste your resume content here...", lines=10)
    output = gr.Textbox(label="Career Advice")
    btn = gr.Button("Get Advice", variant="primary")
    btn.click(fn=get_career_advice, inputs=[position, job_desc, resume], outputs=output)

# --------------------------------------------------------------------------- #
#  Cover Letter Generator                                                     #
# --------------------------------------------------------------------------- #
def generate_cover_letter(company, position, job_desc, resume_content):
    prompt = (
        f"Generate a customized cover letter using the company name: {company}, "
        f"the position applied for: {position}, and the job description: {job_desc}. "
        f"Ensure the cover letter highlights my qualifications and experience as detailed "
        f"in the resume content: {resume_content}. Adapt the content carefully to avoid "
        f"including experiences not present in my resume but mentioned in the job description. "
        f"The goal is to emphasize the alignment between my existing skills and the requirements of the role."
    )

    response = client.chat_completion(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=2048,
    )
    return response.choices[0].message.content

def _cover_letter_tab():
    with gr.Row():
        company = gr.Textbox(label="Company Name", placeholder="Enter the name of the company...")
        position = gr.Textbox(label="Position Name", placeholder="Enter the name of the position...")
    with gr.Row():
        job_desc = gr.Textbox(label="Job Description", placeholder="Paste the job description here...", lines=10)
    with gr.Row():
        resume = gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=10)
    output = gr.Textbox(label="Customized Cover Letter")
    btn = gr.Button("Generate Cover Letter", variant="primary")
    btn.click(fn=generate_cover_letter, inputs=[company, position, job_desc, resume], outputs=output)

# --------------------------------------------------------------------------- #
#  App                                                                        #
# --------------------------------------------------------------------------- #
with gr.Blocks(title="Resume Polisher Suite") as app:
    gr.Markdown("# Resume Polisher Suite\nAI-powered tools to strengthen your job application materials.")

    with gr.Tabs():
        with gr.Tab("Resume Polisher"):
            gr.Markdown("Polish your resume for a specific role. Optionally add custom instructions.")
            _resume_polisher_tab()
        with gr.Tab("HTML Resume"):
            gr.Markdown("Upload a photo and paste your resume to generate a downloadable HTML file.")
            _generate_html_tab()
        with gr.Tab("Cover Letter"):
            gr.Markdown("Generate a tailored cover letter from your resume and the job posting.")
            _cover_letter_tab()
        with gr.Tab("Career Advisor"):
            gr.Markdown("Get targeted advice by comparing your resume against a job description.")
            _career_advisor_tab()

    gr.Markdown("---\n*Powered by Llama 3.2 · Built with Gradio & Hugging Face Inference API*")

app.launch(share=True)
