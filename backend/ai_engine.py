import openai
import os
from dotenv import load_dotenv

# Load API Key from environment variables
load_dotenv()
openai.api_key = os.getenv("--")

def generate_classroom_activity(topic):
    """Generates an engaging classroom activity using OpenAI's GPT model."""
    prompt = f"Suggest an interactive classroom activity to teach the topic: {topic}."

    try:
        client = openai.OpenAI()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[{"role": "user", "content":  f"Generate an engaging classroom activity for {topic}"}],
            max_tokens=100
        )

        activity = response["choices"][0]["message"]["content"].strip()
        return activity

    except Exception as e:
        return f"Error: {str(e)}"




