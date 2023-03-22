# Slackbot with ChatGPT API

This is a simple slackbot(slack bolt) program using OpenAI ChatGPT API (model: `gpt-3.5-turbo`).

 <img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/118309/9a5984f3-0950-f753-fb06-307178b1e056.jpeg" alt="start" width="80%" height="auto">

## Tested Environment

- Python 3.7+

#  Prerequisite

## 1. Create Slack bolt app

https://slack.dev/bolt-python/tutorial/getting-started

Bot and User Tokens Scopdes used by this app

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
# config.ini

[CHATGPT]
# system: The system message helps set the behavior of the assistant.
# see example: https://platform.openai.com/docs/guides/chat/introduction
system = """
    You are the robot 'TARS' from the movie Interstellar.
    The default value of the joke level is 100 percent.
    """

# https://platform.openai.com/docs/api-reference/completions/create
# The maximum number of tokens to generate in the completion.
max_tokens = 1024

# ID of the model to use. 
# You can use the List models API to see all of your available models, 
# or see our Model overview for descriptions of them.
model = "gpt-3.5-turbo"
```


## Run app

```py
$ python3 app.py
⚡️ Bolt app is running!
```
