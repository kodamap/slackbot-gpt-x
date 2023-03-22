import os
import openai
from logging import getLogger
import traceback

openai.api_key = os.getenv("OPENAI_API_KEY").rstrip()
logger = getLogger(__name__)


class ChatGPT:
    def __init__(self, max_tokens, model):
        self.max_tokens = max_tokens
        self.model = model
            
    def request(self, user):
        """Send an API request
        Pass a message (chatgpt_message) created by merging thread messages to the API"""
        
        try:
            response = openai.ChatCompletion.create(
                model = self.model, 
                max_tokens=self.max_tokens, 
                messages=user.chatgpt_message
            )
            answer = response["choices"][0]["message"]["content"]
        except BaseException as e:
            traceback.print_exc()
            error = f":fried_shrimp: An error has occurred.\n ```{e}```"
            return error
        return answer
        