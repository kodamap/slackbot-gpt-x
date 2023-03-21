# base modules
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from logging import getLogger, basicConfig, DEBUG, INFO
import re
from argparse import ArgumentParser

# chat gpt
from chatgpt import ChatGPT

app = App(token=os.environ["SLACK_BOT_TOKEN"])
logger = getLogger(__name__)

# Define class to store user info
class User:
    pass
 
def get_user(message):
    user = User()
    user.user_id = message["user"]
    user.email = app.client.users_info(user=message["user"])["user"]["profile"]["email"]
    user.prompt = message["text"]
    return user

def align_chat(chat, list_history=False, show_all=False):
    """
    chat table does not have chat_id column
    n: limitation of content_size
    type: Change return format when listing history  
    """
    
    alinged_chat = ""
    for c in chat:
        chat_id = c.chat_id
        created_at = c.created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        role, content = c.content["role"], c.content["content"]
        if role == "system":
            continue
        if role == "user":
            role = ":no_mouth:"
        elif role == "assistant":
            role = ":chatgpt:"
        else:
            role = ":question:"
        
        if len(content.strip()) > n and not show_all:
            content = content.strip()[:n] + " ..."

        if list_history:
            alinged_chat += f"`{chat_id}` `{created_at}` | {role} {content}\n"
        else:
            alinged_chat += f"`{created_at}` | {role} {content}\n"
    
    return alinged_chat
    
@app.message("hello")
def message_hello(client, message, say):
    text = f"<@{message['user']}> Hey there!"
    client.chat_postMessage(channel=message["channel"], thread_ts=message["ts"], text=text)
    logger.info(f"Hey there <@{message['user']}>!")


@app.message(re.compile(r"^!start((.|\s)*)$"))
def start_chat(client, message, say):
    # prepare instances
    user = get_user(message)
    user.prompt = message['text'].split("!start")[1].strip()

    chatgpt = ChatGPT(user)
    chatgpt.start(user)
    answer, chat_count = chatgpt.request(user)
    text = f"<@{message['user']}> :left_speech_bubble: `{chat_count-1}` {answer}"
    client.chat_postMessage(channel=message["channel"], thread_ts=message["ts"], text=text)
    logger.info(f"{answer}")

    del chatgpt

@app.message(re.compile(r"^!resume((.|\s)*)$"))
def resume_chat(client, message, say):
    chat_id = ""
    chat_id = message['text'].split("!resume")[1].strip().replace("`","")
    logger.info(f"chat_id:{chat_id}")

    user = get_user(message)
    chatgpt = ChatGPT(user)
    chat_history = chatgpt.resume(user, chat_id)
    
    if not chat_history:
        say(f"<@{message['user']}> Chat history does not exist. Check chat_id:({chat_id}).")
        del chatgpt
        return
    
    text = f"<@{message['user']}> Let's continue the chat. `{chat_id}`"
    client.chat_postMessage(channel=message["channel"], thread_ts=message["ts"], text=text)
    logger.info(f"<@{message['user']}> Let's continue the chat. `{chat_id}`")
    del chatgpt
        
@app.message(re.compile(r"^!list((.|\s)*)$"))
def list_history(client, message, say):
    # prepare instances
    user = get_user(message)
    chatgpt = ChatGPT(user)
    chat_history = chatgpt.list_history(user)
    alinged_chat_history = ""
    for chat in chat_history:
        alinged_chat = align_chat(chat, list_history=True)
        alinged_chat_history += alinged_chat
    
    history_count = len(chat_history)
    text = f"<@{message['user']}> :left_speech_bubble: `History:{history_count} `\n\n{alinged_chat_history}"
    client.chat_postMessage(channel=message["channel"], thread_ts=message["ts"], text=text)
    logger.info(f"<@{message['user']}> History:{history_count}")

    del chatgpt

@app.message(re.compile(r"^!show((.|\s)*)$"))
def show_history(client, message, say, context, logger):
    chat_id = ""
    chat_id = message['text'].split("!show")[1].strip().replace("`","")
    logger.info(f"chat_id:{chat_id}")
    
    user = get_user(message)
    chatgpt = ChatGPT(user)
    
    if chat_id:
        # show old chat conversation history
        header = f"Chat history...\n"
        chat_history = chatgpt.show_history(user, chat_id)
    else:
        # show realtime chat conversation history
        header = f"Chat in progress...\n"
        chat_history = chatgpt.show_history(user, chat_id)
    if not chat_history:
        text = f"<@{message['user']}> Chat history doew not exist. Check chat_id:({chat_id})"
        client.chat_postMessage(channel=message["channel"], thread_ts=message["ts"], text=text)
        logger.info(f"<@{user.user_id}> Chat history doew not exist. Check chat_id:({chat_id}).")
        return
    
    # exclude system role chat
    alinged_chat = align_chat(chat_history, show_all=True)
    alinged_chat = header + alinged_chat

    text = f"<@{message['user']}> :left_speech_bubble: `Chat:{len(chat_history)-1} `\n\n{alinged_chat}"
    client.chat_postMessage(channel=message["channel"], thread_ts=message["ts"], text=text)
    logger.info(f"<@{message['user']}> History:{len(chat_history)-1}")
    del chatgpt
            
@app.message(re.compile(r"^!save((.|\s)*)$"))
def save_history(client, message, say):
    user = get_user(message)
    chatgpt = ChatGPT(user)
    chat_history_count = chatgpt.save_history(user)
    list_history(client, message, say)
    logger.info(f"<@{message['user']}> History:{chat_history_count}")
    del chatgpt

@app.message(re.compile(r"^!delete((.|\s)*)$"))
def delete_history(client, message, say):
    user = get_user(message)
    chatgpt = ChatGPT(user)
    chatgpt.delete_history(user)

    text = f"<@{message['user']}> Chat history have been deleted"
    client.chat_postMessage(channel=message["channel"], thread_ts=message["ts"], text=text)
    logger.info(f"<@{message['user']}> Chat history have been deleted")
    del chatgpt
        
@app.event("message")        
def handle_message_events(client, message, say):
    """
    - Create a chatgpt instance for each conversation.
    - Read chat history from the database.
    - Delete the chatgpt instance when the conversation is finished.
    """
    # prepare instances
    user = get_user(message)
    chatgpt = ChatGPT(user)
    
    # send request
    logger.info(f"<@{message['user']}> request start")
    answer, chat_count = chatgpt.request(user)
    text = f"<@{message['user']}> :left_speech_bubble: `{chat_count-1}` {answer}"
    client.chat_postMessage(channel=message["channel"], thread_ts=message["ts"], text=text)
    logger.info(f"<@{message['user']}> {answer}")

    del chatgpt


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument(
        "-lc",
        "--list_content_size",
        default=100,
        help="output size of content in list command",
        type=int,
    )
    return parser


if __name__ == "__main__":

    basicConfig(
        level=INFO,
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(name)s %(funcName)s(): %(message)s",
    )

    # arg parse
    args = build_argparser().parse_args()
    n = args.list_content_size

    # start slack bolt
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
