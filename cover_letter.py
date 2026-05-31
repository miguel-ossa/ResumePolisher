# Import necessary packages
import os
from huggingface_hub import InferenceClient
import gradio as gr
from dotenv import load_dotenv

load_dotenv(override=True)
hf_token = os.getenv("HF_TOKEN")

# Model and project settings
model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"


# Initialize Hugging Face Inference Client
client = InferenceClient(token=hf_token)

# Function to generate a customized cover letter
def generate_cover_letter(company_name, position_name, job_description, resume_content):
    # Craft the prompt for the model to generate a cover letter
    prompt = f"Generate a customized cover letter using the company name: {company_name}, the position applied for: {position_name}, and the job description: {job_description}. Ensure the cover letter highlights my qualifications and experience as detailed in the resume content: {resume_content}. Adapt the content carefully to avoid including experiences not present in my resume but mentioned in the job description. The goal is to emphasize the alignment between my existing skills and the requirements of the role."

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    # Generate a response using the Hugging Face Inference API
    generated_response = client.chat_completion(
        model=model_id,
        messages=messages,
        temperature=0.7,
        max_tokens=2048
    )

    # Extract and return the generated text
    cover_letter = generated_response.choices[0].message.content

    return cover_letter

# Create Gradio interface for the cover letter generation application
cover_letter_app = gr.Interface(
    fn=generate_cover_letter,
    flagging_mode="never", # Deactivate the flag function in gradio as it is not needed.
    inputs=[
        gr.Textbox(label="Company Name", placeholder="Enter the name of the company..."),
        gr.Textbox(label="Position Name", placeholder="Enter the name of the position..."),
        gr.Textbox(label="Job Description Information", placeholder="Paste the job description here...", lines=10),
        gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=10),
    ],
    outputs=gr.Textbox(label="Customized Cover Letter"),
    title="Customized Cover Letter Generator",
    description="Generate a customized cover letter by entering the company name, position name, job description and your resume."
)

# Launch the application
cover_letter_app.launch()
