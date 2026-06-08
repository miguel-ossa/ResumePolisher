import os
import re
import base64
import tempfile
from huggingface_hub import InferenceClient
import gradio as gr
from dotenv import load_dotenv

load_dotenv(override=True)

# Import model configuration
from config import MODEL_ID

# Configuration flag - if True, use HF_TOKEN from .env; if False, use API key from UI field
USE_ENV_TOKEN = True


def get_error_html(message):
    return f"<div style='color: #d9534f; background-color: #f2dede; padding: 10px; border-radius: 5px; border: 1px solid #ebccd1;'>{message}</div>"

def get_hf_client(token=None):
    """Get InferenceClient instance with the appropriate token."""
    if token:
        # Use provided token (from UI input)
        print("Using Hugging Face token:", token)
        return InferenceClient(token=token)
    elif USE_ENV_TOKEN:
        # Use HF_TOKEN from .env file
        print("Using Hugging Face token from env.")
        hf_token = os.getenv("HF_TOKEN")
        return InferenceClient(token=hf_token)
    else:
        raise ValueError("No Hugging Face token available. Please provide a token via environment variable or UI.")

# --------------------------------------------------------------------------- #
#  Resume Polisher                                                            #
# --------------------------------------------------------------------------- #
def polish_resume(position_name, resume_content, polish_prompt, api_key):
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

    client = get_hf_client(api_key)

    try:
        response = client.chat_completion(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=2048,
        )
        return response.choices[0].message.content, ""
    except Exception as e:
        return "", f"⚠️ Error: {str(e)}. Please check your Hugging Face API key in the Settings tab."

def _resume_polisher_tab(api_key_state):
    with gr.Row():
        position = gr.Textbox(label="Position Name", placeholder="Enter the name of the position...")
    with gr.Row():
        resume = gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=15)
    with gr.Row():
        instructions = gr.Textbox(label="Polish Instructions (Optional)", placeholder="Enter specific areas for improvement...", lines=2)
    output = gr.Textbox(label="Polished Resume")
    error_display = gr.HTML(visible=False)
    btn = gr.Button("Polish Resume", variant="primary")

    def handle_click(pos, res, ins, key):
        res_text, err = polish_resume(pos, res, ins, key)
        if err:
            print("Error:", err)
            return "", gr.update(value=get_error_html(err), visible=True)
        return res_text, gr.update(visible=False)

    # Pass api_key_state as an input to the function
    btn.click(fn=handle_click, inputs=[position, resume, instructions, api_key_state], outputs=[output, error_display])

# --------------------------------------------------------------------------- #
#  Html Generation                                                            #
# --------------------------------------------------------------------------- #
def generate_html(photo, resume, api_key):
    """
    Returns a tuple: (file_path_or_None, error_message)
    """
    try:
        # 1. Convert photo to base64
        photo_html = ""
        if photo:
            try:
                with open(photo, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode("utf-8")
                    mime = "image/png" if photo.lower().endswith(('.png')) else "image/jpeg"
                    photo_data_url = f"data:{mime};base64,{img_data}"
                    photo_html = f'<img src="{photo_data_url}" alt="Profile Photo" style="width: 130px; height: 130px; border-radius: 50%; object-fit: cover; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
            except Exception as e:
                return None, f"⚠️ Error processing photo: {str(e)}"

        # 2. Prepare Prompt
        prompt = f"""
You are an expert HTML/CSS developer. Generate a clean, professional HTML resume.
**CRITICAL – MARKDOWN CONVERSION**: Convert all markdown into proper HTML tags (<strong>, <em>, <ul>, etc.).
**LAYOUT**: Place the exact text `{{{{PHOTO_PLACEHOLDER}}}}` where the profile photo should appear.
Return ONLY raw HTML starting with <!DOCTYPE html>. No markdown code fences.

Resume content:
{resume}
"""
        # 3. Call API
        client = get_hf_client(api_key)
        response = client.chat_completion(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4096,
        )
        html = response.choices[0].message.content

        # 4. Cleanup and Process
        html = re.sub(r"^```html?\s*", "", html, flags=re.MULTILINE)
        html = re.sub(r"\s*```\s*$", "", html, flags=re.MULTILINE)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        if photo_html and "{{PHOTO_PLACEHOLDER}}" in html:
            html = html.replace("{{PHOTO_PLACEHOLDER}}", photo_html)

        # 5. Save File
        fd, path = tempfile.mkstemp(suffix=".html", text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(html)

        # SUCCESS: Return the path and an empty error string
        return path, ""

    except Exception as e:
        # FAILURE: Return None for the file and the error message
        return None, f"⚠️ Error: {str(e)}. Please check your Hugging Face API key in the Settings tab."

def _generate_html_tab(api_key_state):
    with gr.Row():
        photo = gr.Image(label="Profile Photo", type="filepath", height=200)
    with gr.Row():
        resume = gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=15)

    # UI Components
    output_file = gr.File(label="Download HTML Resume")
    error_display = gr.HTML(visible=False)
    btn = gr.Button("Generate HTML", variant="primary")

    def handle_click(photo, resume, key):
        path, err = generate_html(photo, resume, key)
        if err:
            print("Error:", err)
            return gr.update(value=None, visible=False), gr.update(value=get_error_html(err), visible=True)
        else:
            return gr.update(value=path, visible=True), gr.update(visible=False)

    btn.click(
        fn=handle_click,
        inputs=[photo, resume, api_key_state],
        outputs=[output_file, error_display]
    )

# --------------------------------------------------------------------------- #
#  Career Advisor                                                             #
# --------------------------------------------------------------------------- #
def get_career_advice(position, job_desc, resume_content, api_key):
    prompt = (
        f"Considering the job description: {job_desc}, and the resume provided: "
        f"{resume_content}, identify areas for enhancement in the resume. Offer specific "
        f"suggestions on how to improve these aspects to better match the job requirements "
        f"and increase the likelihood of being selected for the position of {position}."
    )

    client = get_hf_client(api_key)

    try:
        response = client.chat_completion(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1024,
        )
        return response.choices[0].message.content, ""
    except Exception as e:
        return "", f"⚠️ Error: {str(e)}. Please check your Hugging Face API key in the Settings tab."

def _career_advisor_tab(api_key_state):
    with gr.Row():
        position = gr.Textbox(label="Position Applied For", placeholder="Enter the position you are applying for...")
    with gr.Row():
        job_desc = gr.Textbox(label="Job Description", placeholder="Paste the job description here...", lines=10)
    with gr.Row():
        resume = gr.Textbox(label="Your Resume Content", placeholder="Paste your resume content here...", lines=10)
    output = gr.Textbox(label="Career Advice")
    error_display = gr.HTML(visible=False)
    btn = gr.Button("Get Advice", variant="primary")

    def handle_click(pos, desc, res, key):
        advice, err = get_career_advice(pos, desc, res, key)
        if err:
            print("Error:", err)
            return "", gr.update(value=get_error_html(err), visible=True)
        return advice, gr.update(visible=False)

    btn.click(fn=handle_click, inputs=[position, job_desc, resume, api_key_state], outputs=[output, error_display])

# --------------------------------------------------------------------------- #
#  Cover Letter Generator                                                     #
# --------------------------------------------------------------------------- #
def generate_cover_letter(company, position, job_desc, resume_content, api_key):
    prompt = (
        f"Generate a customized cover letter using the company name: {company}, "
        f"the position applied for: {position}, and the job description: {job_desc}. "
        f"Ensure the cover letter highlights my qualifications and experience as detailed "
        f"in the resume content: {resume_content}."
    )

    client = get_hf_client(api_key)

    try:
        response = client.chat_completion(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=2048,
        )
        return response.choices[0].message.content, ""
    except Exception as e:
        return "", f"⚠️ Error: {str(e)}. Please check your Hugging Face API key in the Settings tab."

def _cover_letter_tab(api_key_state):
    with gr.Row():
        company = gr.Textbox(label="Company Name", placeholder="Enter the name of the company...")
        position = gr.Textbox(label="Position Name", placeholder="Enter the name of the position...")
    with gr.Row():
        job_desc = gr.Textbox(label="Job Description", placeholder="Paste the job description here...", lines=10)
    with gr.Row():
        resume = gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=10)
    output = gr.Textbox(label="Customized Cover Letter")
    error_display = gr.HTML(visible=False)
    btn = gr.Button("Generate Cover Letter", variant="primary")

    def handle_click(comp, pos, desc, res, key):
        letter, err = generate_cover_letter(comp, pos, desc, res, key)
        if err:
            print("Error:", err)
            return "", gr.update(value=get_error_html(err), visible=True)
        return letter, gr.update(visible=False)

    btn.click(fn=handle_click, inputs=[company, position, job_desc, resume, api_key_state],
              outputs=[output, error_display])

# --------------------------------------------------------------------------- #
#  Settings                                                                   #
# --------------------------------------------------------------------------- #
def update_api_key(new_key, current_state):
    # Update the state with the new key
    return new_key

def _settings_tab(api_key_state):
    with gr.Row():
        input_key = gr.Textbox(label="Hugging Face API Key", placeholder="Enter your Hugging Face API key here...", type="password")

    btn = gr.Button("Update API Key", variant="primary")

    # When button is clicked, update the state variable
    btn.click(fn=update_api_key, inputs=[input_key, api_key_state], outputs=api_key_state)
    gr.Markdown("Click 'Update API Key' to apply the new key to your current session.")

# --------------------------------------------------------------------------- #
#  App                                                                        #
# --------------------------------------------------------------------------- #
with gr.Blocks(title="Resume Polisher Suite") as app:
    # Initialize the session state with the environment variable (if available)
    if USE_ENV_TOKEN:
        api_key_state = gr.State(value=os.getenv("HF_TOKEN"))
    else:
        api_key_state = gr.State(value="dummy")

    gr.Markdown("# Resume Polisher Suite\nAI-powered tools to strengthen your job application materials.")

    with gr.Tabs():
        with gr.Tab("Resume Polisher"):
            gr.Markdown("Polish your resume for a specific role.")
            _resume_polisher_tab(api_key_state)
        with gr.Tab("HTML Resume"):
            gr.Markdown("Upload a photo and paste your resume to generate a downloadable HTML file.")
            _generate_html_tab(api_key_state)
        with gr.Tab("Cover Letter"):
            gr.Markdown("Generate a tailored cover letter from your resume and the job posting.")
            _cover_letter_tab(api_key_state)
        with gr.Tab("Career Advisor"):
            gr.Markdown("Get targeted advice by comparing your resume against a job description.")
            _career_advisor_tab(api_key_state)
        with gr.Tab("Settings"):
            gr.Markdown("Adjust your settings.")
            _settings_tab(api_key_state)

    gr.Markdown("---\n*Powered by Llama 3.3 · Built with Gradio & Hugging Face Inference API*")

app.launch(share=True)
