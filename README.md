# Slackbot with ChatGPT API

This is a simple slackbot(slack bolt) program using OpenAI ChatGPT API (model: `gpt-3.5-turbo`).

Functions are:


| Function | Command | Description |
|----| -----| ---- |
| Chat with ChatGPT |`!start <chat>` | Clear the ongoing chats history and start a new chat with ChatGPT |
| Save the chat |`!save` | Save chat history. (It will also be saved in the Slack thread, but this saved data will be used when resuming the conversation) |
| Display a list of past chats | `!list` | Display a list of saved chats. The first question becomes the title. |
| show the content of the chat | `!show <chat_id>` | Show the contents of a chat by specifying the chat. | 
| resume a past chat | `!resume <chat_id>` | Resume a chat with ChatGPT from a saved chat history. Restore the history ('role, content`) stored in the database to the data for API requests. |
| delete all past history | `!delete` | Delete all past history |


## Command example 

- __Star chat__

  <img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/118309/c6fbaaf4-4f94-756f-5291-234db10d8144.jpeg" alt="start" width="75%" height="auto">

- __List__

    <img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/118309/6ccade11-baa1-d23d-8475-c5c721813ef8.jpeg" alt="list" width="75%" height="auto">

- __Resume/Show__

    <img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/118309/fc2a2936-550c-6d75-ffd0-01fa7268c7a1.jpeg" alt="resume" width="75%" height="auto">


## Tested Environment

- Python 3.7+

#  Prerequisite

## 1. Create Slack bolt app

https://slack.dev/bolt-python/tutorial/getting-started

Bot Tokens Scopdes used by this app

| OAuth Scope | Description    |
| ----------- | --------------| 
| `channels:history` | View messages and other content in public channels that chatgpt has been added to | 
| `chat:write` | Send messages as @chatgpt |
| `groups:history` | View messages and other content in private channels that chatgpt has been added to |
| `im:history` | View messages and other content in direct messages that chatgpt has been added to |
| `mpim:history` | View messages and other content in group direct messages that chatgpt has been added to |
| `users:read.email` | View email addresses of people in a workspace |


## 2. Create OpenAI API Key

https://platform.openai.com/account/api-keys)


# Packages

```sh
cd slackbot-gpt-x
pip install -r requirements.txt
```


# How to use

## Set your environment variables

```sh
export SLACK_BOT_TOKEN=xoxb-<your token>
export SLACK_APP_TOKEN=xapp-1-<your token>
export OPENAI_API_KEY=sk-<your key>
```

## Setup system role content

```sh
# confit.ini
[CHATGPT]
# system: The system message helps set the behavior of the assistant.
# see example: https://platform.openai.com/docs/guides/chat/introduction
system = """
    You are the robot 'TARS' from the movie Interstellar.
    The default value of the joke level is 100 percent.
    """
max_tokens = 1024
```


## Run app

```py
$ python3 app.py
⚡️ Bolt app is running!
```
