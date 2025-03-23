import openai
import os
from dotenv import load_dotenv

# Load API Key from environment variables
load_dotenv()
openai.api_key = os.getenv("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")

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




