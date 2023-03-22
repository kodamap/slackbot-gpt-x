# base modules
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from logging import getLogger, basicConfig, DEBUG, INFO

# chat gpt
import configparser
from chatgpt import ChatGPT

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")
system_content = eval(config.get("CHATGPT", "system"))
max_tokens = eval(config.get("CHATGPT", "max_tokens"))
model = eval(config.get("CHATGPT", "model"))

# craete app and logger instance
app = App(token=os.environ["SLACK_BOT_TOKEN"])
logger = getLogger(__name__)

# Prepare an empty class to have properties later.
class User:
    pass

def get_user(message, client):
    """
    Set data for this app to User instance.
    """
    user = User()
    user.user_id = message.get("user")
    user.email = client.users_info(user=message["user"])["user"]["profile"]["email"]
    user.prompt = message.get("text")
    user.thread_ts = message.get("thread_ts")
    user.ts = message.get("ts")
    return user

def create_chatgpt_message(response):
    """
    Create a message for ChatGPT API from the thread content. 
    If app_id is present, it is assumed to be a response from ChatGPT, 
    set "assistant" role. If not, set "user" role.
    """
    thread_ts = response.data['messages'][0].get('thread_ts')
    content = {"role": "system", "content": system_content}
    chatgpt_message = {thread_ts: {'message': [content], 'time_stamp': []}}

    for res in response.data['messages']:
        app_id = res.get('app_id')
        role = "assistant" if app_id else "user"
        text = res.get('text')
        time_stamp = res.get('ts')
        content = {"role": role, "content": text}
        chatgpt_message[thread_ts]['message'].append(content)
        chatgpt_message[thread_ts]['time_stamp'].append(time_stamp)

    return chatgpt_message

@app.event("message")        
def handle_message_events(client, message, say):
    """
    New messages will be threaded.
    Messages in threads are retrieved with `conversatins_replies`, 
    and then requesed in the format passed to ChatGPT API.
    The replies are returned to the same thread.
    """

    # message does not contain 'user' when deleting message
    if message.get('user') is None:
        return 

    # prepare instances
    user = get_user(message, client)
    chatgpt = ChatGPT(max_tokens, model)
    
    # send request
    logger.info(f"{user.email} request start")

    # An existing thread has thread_ts key
    if message.get('thread_ts'):
        thread_ts = message.get('thread_ts')
    # New thread 
    else:
        thread_ts = message.get('ts')

    response = client.conversations_replies(channel=message["channel"], ts=thread_ts)
    chatgpt_message = create_chatgpt_message(response)

    # Add created chatgpt message for api request as a User instance's property
    user.chatgpt_message = chatgpt_message[user.thread_ts]['message']
    logger.info(f"user_id:{user.user_id} email:{user.email} thread_ts:{user.thread_ts} ts:{user.ts} chat:{user.chatgpt_message}")
    answer = chatgpt.request(user)

    # Send answer from chatgpt api response
    ##text = f"<@{message['user']}> {answer}"
    ##client.chat_postMessage(channel=message["channel"], thread_ts=thread_ts, text=text)
    client.chat_postMessage(channel=message["channel"], thread_ts=thread_ts, text=answer)
    logger.info(f"{user.email} {answer}")

    del user
    del chatgpt


if __name__ == "__main__":

    basicConfig(
        level=INFO,
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(name)s %(funcName)s(): %(message)s",
    )

    # start slack bolt
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
