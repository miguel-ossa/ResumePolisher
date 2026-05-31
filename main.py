"""Unified entry point for the Resume Polisher suite.

Launches a single Gradio app with three tabs:
  - Resume Polisher
  - Career Advisor
  - Cover Letter Generator

Each tab reuses the logic from its respective module while sharing
a single Hugging Face InferenceClient instance.

Usage:
    python main.py
"""

import os
from huggingface_hub import InferenceClient
import gradio as gr
from dotenv import load_dotenv

load_dotenv(override=True)
hf_token = os.getenv("HF_TOKEN")

# Shared model and client
MODEL_ID = "meta-llama/Llama-3.2-11B-Vision-Instruct"
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
        temperature=0.7,
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
        temperature=0.7,
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
        temperature=0.7,
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
        with gr.Tab("Career Advisor"):
            gr.Markdown("Get targeted advice by comparing your resume against a job description.")
            _career_advisor_tab()
        with gr.Tab("Cover Letter"):
            gr.Markdown("Generate a tailored cover letter from your resume and the job posting.")
            _cover_letter_tab()

    gr.Markdown("---\n*Powered by Llama 3.2 · Built with Gradio & Hugging Face Inference API*")

app.launch()
