import google.generativeai as genai 
import os

from utils.constants import GENERAL_CONVERSATION

class GeneralConv:
    def __init__(self):        
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        self.context = open(GENERAL_CONVERSATION, "r").read()
    
    def general_response(self, user_question: str):
        update_context = self.context.replace(
            "{User Message}", user_question
        )
        response = self.model.generate_content(update_context)
        return response.text

