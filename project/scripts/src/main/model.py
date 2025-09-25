import google.generativeai as genai
import os
from dotenv import load_dotenv

class LLMInterface:
    def __init__(self):
        load_dotenv()
        # Configure the API key for authentication
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Initialize the Gemini 2.5 Flash model
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate(self, question: str) -> str:

        response = self.model.generate_content(question)
        return response.text