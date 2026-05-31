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

# Function to polish the resume using the model, making polish_prompt optional
def polish_resume(position_name, resume_content, polish_prompt=""):
    # Check if polish_prompt is provided and adjust the prompt accordingly
    if polish_prompt and polish_prompt.strip():
        prompt_use = f"Given the resume content: '{resume_content}', polish it based on the following instructions: {polish_prompt} for the {position_name} position."
    else:
        prompt_use = f"Suggest improvements for the following resume content: '{resume_content}' to better align with the requirements and expectations of a {position_name} position. Return the polished version, highlighting necessary adjustments for clarity, relevance, and impact in relation to the targeted role."

    messages = [
        {
            "role": "user",
            "content": prompt_use,
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
    generated_text = generated_response.choices[0].message.content

    return generated_text


# Create Gradio interface for the resume polish application, marking polish_prompt as optional
resume_polish_application = gr.Interface(
    fn=polish_resume,
    flagging_mode="never",  # Deactivate the flag function in gradio as it is not needed.
    inputs=[
        gr.Textbox(label="Position Name", placeholder="Enter the name of the position..."),
        gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=20),
        gr.Textbox(label="Polish Instruction (Optional)",
                   placeholder="Enter specific instructions or areas for improvement (optional)...", lines=2),
    ],
    outputs=gr.Textbox(label="Polished Content"),
    title="Resume Polish Application",
    description="This application helps you polish your resume. Enter the position your want to apply, your resume content, and specific instructions or areas for improvement (optional), then get a polished version of your content."
)

# Launch the application
resume_polish_application.launch()
