# base modules
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from logging import getLogger, basicConfig, INFO

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


def create_chat_history(response, thread_ts):
    """
    Create a message for ChatGPT API from the thread content.
    If app_id is present, it is assumed to be a response from ChatGPT,
    set "assistant" role. If not, set "user" role.
    """
    content = {"role": "system", "content": system_content}
    chat_history = {thread_ts: {"message": [content], "time_stamp": []}}

    for res in response.data["messages"]:
        app_id = res.get("app_id")
        role = "assistant" if app_id else "user"
        text = res.get("text")
        time_stamp = res.get("ts")
        content = {"role": role, "content": text}
        chat_history[thread_ts]["message"].append(content)
        chat_history[thread_ts]["time_stamp"].append(time_stamp)

    return chat_history


@app.event("message")
def handle_message_events(client, message):
    """
    New messages will be threaded.
    Messages in threads are retrieved with `conversatins_replies`,
    and then requesed in the format passed to ChatGPT API.
    The replies are returned to the same thread.
    """

    # message does not contain 'user' when deleting message
    if message.get("user") is None:
        return

    # Create ChatGPT instances
    chatgpt = ChatGPT(max_tokens, model)

    # An existing thread has thread_ts key
    if message.get("thread_ts"):
        thread_ts = message.get("thread_ts")
    # New thread
    else:
        thread_ts = message.get("ts")

    # Get thread messages and create messages for chatgpt request
    response = client.conversations_replies(channel=message["channel"], ts=thread_ts)
    chat_history = create_chat_history(response, thread_ts)

    # Add created chatgpt message for api request as a User instance's property
    chat_history = chat_history[thread_ts]["message"]
    logger.info(f"user_id:{message['user']} thread_ts:{thread_ts} chat:{chat_history}")

    # Sent request to chatgpt
    answer = chatgpt.request(chat_history)
    logger.info(f"user_id:{message['user']} thread_ts:{thread_ts}  chat:{answer}")
    client.chat_postMessage(
        channel=message["channel"], thread_ts=thread_ts, text=answer
    )

    del chatgpt


if __name__ == "__main__":
    basicConfig(
        level=INFO,
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(name)s %(funcName)s(): %(message)s",
    )

    # start slack bolt
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
