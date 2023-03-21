import os
import openai
from logging import getLogger
import traceback
import configparser

# database for chat history
from db.models import Chat, ChatHistory
from db.settings import session
from sqlalchemy import distinct

openai.api_key = os.getenv("OPENAI_API_KEY").rstrip()
logger = getLogger(__name__)


config = configparser.ConfigParser()
config.read("config.ini")

content = eval(config.get("CHATGPT", "system"))
max_tokens = eval(config.get("CHATGPT", "max_tokens"))

class ChatGPT:
    def __init__(self, user):
        """If there is no conversation for the user,
        add the system role content and store it into the chat table
        """           
        if not self._get(user):
            # Insert first record
            self._save(user, role="system", content=content)
            
    def _get(self, user):
        return session.query(Chat).filter_by(email=user.email).all()
    
    def _get_history(self, user, chat_id):
        return session.query(ChatHistory).filter_by(email=user.email, chat_id=chat_id).all()
    
    def _save(self, user, role=None, content=""):
        """Update record by adding question `user` and answer `assistant"""
        chat = Chat()
        chat.user_id = user.user_id
        chat.email = user.email
        chat.content = {"role": role, "content": content}
        session.add(instance=chat)
        session.commit()
    
    def _reset(self, user):
        """Reset the lastconversation history（delete the chatdb record)"""
        session.query(Chat).filter_by(email=user.email).delete()
        session.commit()
        self.__init__(user)
        logger.info(f"Chat has been reset. user:{user.email}")
         
    def _create_message(self, chat):
        message = []
        for c in chat:
            message.append(c.content)
        return message
    
    def start(self, user):
        chat = self._get(user)
        if chat:
            self._reset(user)
        self.__init__(user)
    
    def resume(self, user, chat_id):
        """
        Replace ongoing conversations with historical ones
        """
        session.query(Chat).filter_by(email=user.email).delete()
        session.commit()
        chat = self._get_history(user, chat_id)
        if not chat:
            return
        for c in chat:
            self._save(user, role=c.content['role'], content=c.content['content'])
        return chat
    
    def request(self, user):
        """Send an API request
        Questions and answers are appended to the conversation history and stored in the `assistant` role"""
        
        self._save(user, role="user", content=user.prompt)
        chat = self._get(user)
        message = self._create_message(chat)
        logger.info(f"{user.email} {user.prompt}")
        
        # request
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                max_tokens=max_tokens, 
                messages=message
            )
            answer = response["choices"][0]["message"]["content"]
        except BaseException as e:
            traceback.print_exc()
            error = f":fried_shrimp: An error has occurred.\n ```{e}```"
            return error
        
        self._save(user, role="assistant", content=answer)
        chat_count = session.query(Chat).filter_by(email=user.email).count()
        logger.info(f"{user.email} {answer}")
        return answer, chat_count
        
    def save_history(self, user):      
        chat = self._get(user)
        chat_history_count= session.query(distinct(ChatHistory.chat_id)).filter_by(email=user.email).count() 
        # Insert history
        for c in chat:
            chat_history = ChatHistory()
            chat_id = c.user_id + str(chat_history_count+1).zfill(5)
            chat_history.chat_id = chat_id
            chat_history.email = c.email
            chat_history.user_id = c.user_id
            chat_history.content = c.content
            chat_history.created_at = c.created_at
            session.add(instance=chat_history)
        session.commit()
        chat_history_count= session.query(distinct(ChatHistory.chat_id)).filter_by(email=user.email).count() 
        return chat_history_count
    
    def list_history(self, user):
        
        chat_ids = session.query(distinct(ChatHistory.chat_id)).filter_by(email=user.email).all()
        history = []
        for chat_id in chat_ids:
            chat_content = session.query(ChatHistory).filter_by(email=user.email, chat_id=chat_id[0]).all()
            if len(chat_content) > 1:
                # return 2 line of user role
                history.append(chat_content[:2])
        return history
        
    def show_history(self, user, chat_id):
        if chat_id:
            return session.query(ChatHistory).filter_by(email=user.email, chat_id=chat_id).all()
        else:
            return session.query(Chat).filter_by(email=user.email).all()
    
    def delete_history(self, user):
        """Reset the lastconversation history(delete the chatdb record)"""
        session.query(ChatHistory).filter_by(email=user.email).delete()
        session.commit()
        logger.info(f"Chat history has been reset. user:{user.email}")