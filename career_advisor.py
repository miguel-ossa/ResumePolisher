# Import necessary packages
import os
from huggingface_hub import InferenceClient
import gradio as gr
from dotenv import load_dotenv

load_dotenv(override=True)
hf_token = os.getenv("HF_TOKEN")

# Model settings
model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"

# Initialize Hugging Face Inference Client
client = InferenceClient(token=hf_token)


# Function to generate career advice
def generate_career_advice(position_applied, job_description, resume_content):
    # The prompt for the model
    prompt = f"Considering the job description: {job_description}, and the resume provided: {resume_content}, identify areas for enhancement in the resume. Offer specific suggestions on how to improve these aspects to better match the job requirements and increase the likelihood of being selected for the position of {position_applied}."

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
        max_tokens=1024
    )

    # Extract and return the generated text
    advice = generated_response.choices[0].message.content
    return advice


# Create Gradio interface for the career advice application
career_advice_app = gr.Interface(
    fn=generate_career_advice,
    flagging_mode="never",  # Deactivate the flag function in gradio as it is not needed.
    inputs=[
        gr.Textbox(label="Position Applied For", placeholder="Enter the position you are applying for..."),
        gr.Textbox(label="Job Description Information", placeholder="Paste the job description here...", lines=10),
        gr.Textbox(label="Your Resume Content", placeholder="Paste your resume content here...", lines=10),
    ],
    outputs=gr.Textbox(label="Advice"),
    title="Career Advisor",
    description="Enter the position you're applying for, paste the job description, and your resume content to get advice on what to improve for getting this job."
)

# Launch the application
career_advice_app.launch()
