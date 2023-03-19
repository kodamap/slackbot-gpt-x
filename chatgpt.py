import os
import openai
from logging import getLogger
import traceback
import configparser

openai.api_key = os.getenv("OPENAI_API_KEY").rstrip()
logger = getLogger(__name__)


config = configparser.ConfigParser()
config.read("config.ini")

content = eval(config.get("CHATGPT", "system"))
max_tokens = eval(config.get("CHATGPT", "max_tokens"))


class ChatGPT:
    def __init__(self, user, session, chatdb):
        """If there is no conversation history for the user,
        add the system role content and store it in the conversation history
        """
        if session.query(chatdb).filter_by(user=user).first() is None:
            # define system content
            system_role = [{"role": "system", "content": content}]
            # Insert history
            chat = chatdb()
            chat.user = user
            chat.chat = system_role
            session.add(instance=chat)
            session.commit()

    def get(self, user, session, chatdb):
        """Obtain information from conversation history table"""
        if session.query(chatdb).filter_by(user=user).first() is None:
            return None, None
        else:
            result = session.query(chatdb).filter_by(user=user).first()
        return result.user, result.chat

    def reset(self, user, session, chatdb):
        """Reset conversation history （delete record)"""

        if session.query(chatdb).filter_by(user=user).first() is None:
            return
        session.query(chatdb).filter_by(user=user).delete()
        session.commit()
        logger.info(f"Chat history has been reset. user:{user}")

    def send(self, user, prompt, session, chatdb, save=True):
        """Send an API request
        Questions and answers are appended to the conversation history and stored in the `assistant` role"""
        _, chat = self.get(user, session, chatdb)
        chat.append({"role": "user", "content": prompt})

        if save:
            self.save(user, prompt, session, chatdb, role="user")

        # Api request
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", max_tokens=max_tokens, messages=chat
            )
        except BaseException as e:
            traceback.print_exc()
            error = f":fried_shrimp: An error has occurred.\n ```{e}```"
            return error

        answer = response["choices"][0]["message"]["content"]

        if save:
            self.save(user, answer, session, chatdb, role="assistant")

        _, chat = self.get(user, session, chatdb)
        logger.info(f"{user} {chat}")
        return answer

    def save(self, user, content, session, chatdb, role):
        """Update record by adding question `user` and answer `assistant"""
        _, chat = self.get(user, session, chatdb)
        if role == "user":
            chat.append({"role": "user", "content": content})
        if role == "assistant":
            chat.append({"role": "assistant", "content": content})
        if chat:
            db = session.query(chatdb).filter_by(user=user).first()
            db.chat = chat
            session.commit()
