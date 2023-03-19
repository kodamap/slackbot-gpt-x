# ChatGPT Slackbot

This is a simple slackbot(slack bolt) program using OpenAI ChatGPT API (model: `gpt-3.5-turbo`).

Functions are:
1. Chat using ChatGPT API on Slack
1. Show chat history (confirm your chat status)
1. Save chat history (keep the chain of conversation)
1. Reset chat history (start new chat)
1. Reset chat history automatically when it exceed `max_history_size` defined in `confing.ini` (prevent from keeping too many chat history)

__Chat__

<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/118309/1edf9bca-0ca5-d3d2-a864-98f140d944d7.jpeg" alt="chat" width="75%" height="auto">

## Tested Environment

- Python 3.7+

# Prerequiste

## Create Slack bolt app

https://slack.dev/bolt-python/tutorial/getting-started

___Bot Tokens Scopdes used by this app__

| OAuth Scope | Description    |
| ----------- | --------------| 
| `channels:history` | View messages and other content in public channels that chatgpt has been added to | 
| `chat:write` | Send messages as @chatgpt |
| `groups:history | View messages and other content in private channels that chatgpt has been added to |
| `im:history` | View messages and other content in direct messages that chatgpt has been added to |
| `mpim:history` | View messages and other content in group direct messages that chatgpt has been added to |
| `users:read.email` | View email addresses of people in a workspace |


## Create OpenAI API Key

Create OpenAI API key

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




