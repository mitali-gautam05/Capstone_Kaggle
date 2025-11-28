import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing. Please set it in your environment.")

client = Groq(api_key=GROQ_API_KEY)

def ask_groq(prompt, model="llama-3.1-8b-instant", temperature=0.35):
    """
    Send prompt to Groq and return plain text response (string).
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    # Groq returns message object with .content
    return response.choices[0].message.content
