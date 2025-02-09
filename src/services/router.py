import google.generativeai as genai 
import os

from utils.constants import ROUTER_PROMPT

class Router:
    def __init__(self):        
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        self.context = open(ROUTER_PROMPT, "r").read()
    
    def router_response(self, user_question: str):
        update_context = self.context.replace(
            "{User Input Text}", user_question
        )
        response = self.model.generate_content(update_context)
        return response.text.strip().lower()

