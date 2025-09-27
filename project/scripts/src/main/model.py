import google.generativeai as genai
import os

class LLMInterface:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("A Gemini API key must be provided.")
        # Kimlik doğrulama için API anahtarını yapılandır
        genai.configure(api_key=api_key)
        # Gemini 1.5 Flash modelini başlat
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate(self, question: str) -> str:
        response = self.model.generate_content(question)
        return response.text