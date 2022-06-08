# Automated Help Desk
## Setup
Follow the command to clone the project
```
git clone http://FG4/faizan.qazi/slackapp.git
cd slackapp
python -m venv venv
source venv/bin/activate || .\venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
## Setting up the App
> We recommend using a workspace where you won’t disrupt real work getting done. You can create a new one for free [here](https://slack.com/get-started#create)
>
> Authenticate yourself and create a workspace.(Skip if you already have a workspace)
- First thing’s first: before starting with Bolt, you’ll want to create a Slack app [here](https://api.slack.com/apps/new).
- Create NewApp > From Scratch
- Fill in Details
    - App Name
    - Select the Workspace
- Create App

## Tokens and installing apps
Slack apps use OAuth to manage access to Slack’s APIs. When an app is installed, you’ll receive a token that the app can use to call API methods.

- Navigate to the OAuth & Permissions on the left sidebar and scroll down to the Bot Token Scopes section. Click Add an OAuth Scope.
- For now, we’ll add two scopes: 
    - `chat:write`: This grants your app the permission to post messages in channels it’s a member of.
    - `users:read`: Determines a user's currently set custom status by consulting their profile.
- Scroll up to the top of the OAuth & Permissions page and click Install App to Workspace. You’ll be led through Slack’s OAuth UI, where you should allow your app to be installed to your development workspace.
- Once you authorize the installation, you’ll land on the OAuth & Permissions page and see a Bot User OAuth Access Token.
![alt text](./images/bot-token.png)
- Head over to Basic Information and scroll down under the App-Level Token section > Generate Token and Scopes (to generate an app-level token). 
    - Add token name and the `connections:write` scope to this token and save the generated xapp token.
- Navigate to Socket Mode on the left side menu and toggle to enable. ( We will change it to http later )

## Setting up events
- Navigate to Event Subscriptions on the left sidebar and toggle to enable. 
- Under Subscribe to Bot Events > Add Bot User Event > 
    - `message:im`
- Subscribe to events on behalf of users > Add Workspace Event > 
    - `message:im`
    - `user_status_changed`
## We're all set!!!
> Remember to keep all tokens secure.

Create your Env variables
```
export SLACK_APP_TOKEN=<your-app-level-token>
export SLACK_BOT_TOKEN=xoxb-<your-bot-token>
```
Create the app py file
```
# Basic Structure
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```
Run the app `python app.py`

## HelpDesk Automation
Structure
1. Select Relevant Department
    To include more departments, add each in `departments.txt` on a separate line and then create a corresponding file called `DEPARTMENTNAME_categories.txt`.
2. Select Issue Category
    To include new issue categories for existing or newly created department, add them in their respective `DEPARTMENTNAME_categories.txt` file on a separate line.

## Auto Out Of Office Replies
To use this feature set your status as `Out of Office`.
The App will generate a response on your behalf as:
```    
Hi, User!!!
I am Out of Office and will be back on 2022-06-08 14:42:10
```
The time is calculated based on your Status Expiration time.
But if the clear date is not provided our response would be
```
Hi, User!!!
I'll be Out of Office for a while. In case of emergency please reach out to <YOUR_CAREER_MANAGER>. Thanks
```
> The App autoreplies once every 20 unresponded messages per channel during the day.   