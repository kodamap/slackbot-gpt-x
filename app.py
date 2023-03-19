# base modules
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from logging import getLogger, basicConfig, DEBUG, INFO
import re
from argparse import ArgumentParser

# chat gpt
from chatgpt import ChatGPT

# database for chat history
from db.models import Chat
from db.settings import session

app = App(token=os.environ["SLACK_BOT_TOKEN"])
logger = getLogger(__name__)


@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")
    user = app.client.users_info(user=message["user"])["user"]["profile"]["email"]
    logger.info(f"{user}")


@app.message(re.compile(r"^!show hist((.|\s)*)$"))
def reset_chat(message, say):
    # user = message["user"]
    user = app.client.users_info(user=message["user"])["user"]["profile"]["email"]
    # create ChatGPT instance
    chatgpt = ChatGPT(user, session, Chat)
    user, chat = chatgpt.get(user, session, Chat)
    history = ""

    for c in chat:
        role, content = c["role"], c["content"]
        if role == "system":
            continue

        if role == "user":
            role = "You"
        elif role == "assistant":
            role = "Bot"
        else:
            role = "Unknown"

        history += f"`{role}`: 「{content}」\n"

    say(
        f"<@{message['user']}> :left_speech_bubble: `Chat history: {len(chat)-1}`\n\n{history}"
    )
    logger.info(f"{user}")

    del chatgpt


@app.message(re.compile(r"^!new chat((.|\s)*)$"))
def reset_chat(message, say):
    user = app.client.users_info(user=message["user"])["user"]["profile"]["email"]
    # create ChatGPT instance
    chatgpt = ChatGPT(user, session, Chat)
    # reset history record of a user
    chatgpt.reset(user, session, Chat)
    say(f"<@{message['user']}> Reset chat history")
    del chatgpt


@app.event("message")
def handle_message_events(message, say):
    """
    - Create a chatgpt instance for each conversation.
    - Read chat history from the database.
    - Delete the chatgpt instance when the conversation is finished.
    """
    user = app.client.users_info(user=message["user"])["user"]["profile"]["email"]
    prompt = message["text"]

    # create ChatGPT instance
    chatgpt = ChatGPT(user, session, Chat)
    # send request
    answer = chatgpt.send(user, prompt, session, Chat)
    # send chat history
    user, chat = chatgpt.get(user, session, Chat)
    say(
        f"<@{message['user']}> :left_speech_bubble: `Chat history: {len(chat)-1}` You can check them by `!show hist` command.\n\n{answer}"
    )
    logger.info(f"{user} history_length:{len(chat)}")
    # Reset caht history if chat history records exceed max_history_size
    if len(chat) - 1 > max_history_size:
        chatgpt.reset(user, session, Chat)

    del chatgpt


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--history_size",
        default=10,
        help="chat history size this app can keep",
        type=int,
    )
    return parser


if __name__ == "__main__":

    basicConfig(
        level=INFO,
        format="%(asctime)s %(levelname)s %(name)s %(funcName)s(): %(message)s",
    )

    # arg parse
    args = build_argparser().parse_args()
    max_history_size = args.history_size

    # start slack bolt
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
