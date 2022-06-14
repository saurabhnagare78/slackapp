# Automated Help Desk

## Prerequisites: 
    
    - Slack Account/Workspace
    - JIRA Account 
## Description

    - This Slack App helps create Jira Tickets from within Slack App Shortcuts (app.py)
    - It also responds to messages when status set as `Out of Office`. (app_autoresp.py)

## Setup
Follow the commands to clone the project
```
git clone git@github.com:caxefaizan/slackapp.git
cd slackapp
python -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
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

## Tokens and Installing apps
> For HTTP Mode we will have to add `Redirect URLs` as well`.

Visit [here](https://api.slack.com/apps) to manage your apps.
Slack apps use OAuth to manage access to Slack’s APIs. When an app is installed, you’ll receive a token that the app can use to call API methods.

- Navigate to the OAuth & Permissions on the left sidebar and scroll down to the Bot Token Scopes section. Click Add an OAuth Scope.
- lets add the scopes: 
    - `chat:write`: This grants your app the permission to post messages in channels it’s a member of.
    - `users:read`: Determines a user's currently set custom status by consulting their profile.
    - `users:write`: Set a user’s presence
    - `im:history`: View messages and other content in a user’s direct messages
    - `im:read`: View basic information about a user’s direct messages
> Read more about scopes and API methods [here](https://api.slack.com/methods).

<p align="center">
    <img src="./images/scopes.png"/>
</p>

- Scroll up to the top of the OAuth & Permissions page and click Install App to Workspace. You’ll be led through Slack’s OAuth UI, where you should allow your app to be installed to your development workspace.
- Once you authorize the installation, you’ll land on the OAuth & Permissions page and see a Bot User OAuth Access Token.

<p align="center">
    <img src="./images/bot-token.png"/>
</p>

- Head over to Basic Information and scroll down under the App-Level Token section > Generate Token and Scopes (to generate an app-level token). 
    - Add token name and the `connections:write` scope to this token and save the generated xapp token.
- Navigate to Socket Mode on the left side menu and toggle to enable. ( We will change it to http later )

## Setting up events
> For HTTP mode we will have to add a `Request URL` as well.
- Navigate to Event Subscriptions on the left sidebar and toggle to enable. 
- Under Subscribe to Bot Events > Add Bot User Event > 
    - `message:im`
- Subscribe to events on behalf of users > Add Workspace Event > 
    - `message:im`
    - `user_status_changed`

<p align="center">
    <img src="./images/events.png"/>
</p>

## App Settings
- App Home > Enable Messages Tab
- Interactivity & Shortcuts > Enable
- Create Shortcut with the following details 
```
Name        Location    Callback ID
Help Desk   Global      caxe_app_shortcut
```
> <span style="color:red;">**Important :**</span> The **`callback id`** reflects in the [app.py](./app.py) as well. Make necessary changes if required.

<p align="center">
    <img src="./images/shortcuts.png"/>
</p>

> Remember to keep all tokens secure.

Use a `config.ini` file to store all tokens and ids.

```
# A typical config file.
[config]
KEY1 = VALUE1
KEY2 = VALUE2
```

Create the [app.py](./app.py) file.
```
# eg. app.py
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

## HelpDesk Automation
### Structure for Form Generation
1. Departments

    To include more departments, add each in `departments.txt` on a separate line and then create a corresponding file called `DEPARTMENTNAME_categories.txt`.
2. Categories

    To include new issue categories for existing or newly created department, add them in their respective `DEPARTMENTNAME_categories.txt` file on a separate line.

## JIRA Setup
- Login to your Jira Account
- Go to your account settings > Security > API Tokens > Create and Manage Tokens > Create Api Token > Copy it and store it in your `config.ini` file. (You wont be able to see it again)
```
# config.ini
[jira]
JIRA_TOKEN = YOUR_TOKEN
JIRA_URL = YOUR_JIRA_URL/rest/api/2/issue/
JIRA_USERNAME = YOUR_JIRA_USERNAME
```
Create a New Project (HR). It reflects in `app.py`

```
ticket_data = {
    "fields": {
        "project": {
            "key": "HR"
        }
```
- Project Settings > Create Rule
- Actor > Automation for Jira
    - When: Issue Created
    - Then: Assign issue
        - Assign the issue to > A user in a defined list
        - Method to choose assignee > Balanced workload
        - JQL to restrict issues > statusCategory != Done
        - User list > HR1, HR2, HR3

<p align="center">
    <img src="./images/jira.png"/>
</p>
- Apps > Slack Integration
<p align="center">
    <img src="./images/jira2.png"/>
</p>

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

## We're all set!!!
Run the app `python3 app.py` for Help Desk
Run the app `python3 app_autoresp.py` for Auto Replies
These can be merged as well.

# HTTP Mode (Disable Socket Mode)
## Install ngrok
```
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
      sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
      echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
      sudo tee /etc/apt/sources.list.d/ngrok.list && \
      sudo apt update && sudo apt install ngrok
```
## Connect your agent to your ngrok account
Now that the ngrok agent is installed, let's connect it to your ngrok [Account](https://dashboard.ngrok.com/). If you haven't already, sign up (or log in) to the ngrok Dashboard and get your Authtoken.

Copy the value and run this command to add the authtoken in your terminal.
```
ngrok config add-authtoken TOKEN
```
- Start Bolt `python app.py`
- Startk ngrok `ngrok http 3000`
- Append the forwarding link with /slack/install
    - eg. `https://46db-49-36-200-218.ngrok.io/slack/install`
    - Authorize the installation and you are good to go.

# Production
Once everything is tested and you want to deploy the app on your domain, deploy it on a flask app using WSGI.

    python3 -m pip flask requests gunicorn

## Creating a Flask Application to Run Your Slackapp
First adjust your firewall settings to allow traffic through port 3000:

    sudo ufw allow 3000

Now check the status of ufw:
    
    sudo ufw status
Now add the following import statements. 
```
# app.py contd.

from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/slack/install", methods=["GET"])
def install():
    return handler.handle(request)

@flask_app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    return handler.handle(request)
```
Finally, create a main section that will launch the app on your external IP address on port 3000. 
```
if __name__ == "__main__":
    # Run your app on your externally facing IP address on port 3000 instead of
    # running it on localhost, which is traditional for development.
    flask_app.run(host='0.0.0.0', port=3000)
```
## Running Your Flask App
Configure your Slack App to use your server's ip address.

- Click on Event Subscriptions in the UI sidebar.
- Once you’ve done that, type in your IP address, port, and `/slack/events` endpoint into the Request URL field. Don’t forget the HTTP protocol prefix. Slack will make an attempt to connect to your endpoint. Once it has successfully done so you’ll see a green check mark with the word Verified next to it.
<p align="center">
    <img src="./images/requesturl.png"/>
</p>

Once you are done developing your application and you are ready to move it to production, you’ll need to deploy it to a server. This is necessary because the Flask development server is not a secure production environment. You’ll be better served if you deploy your app using a WSGI

## Creating the WSGI Entry Point
Next, let’s create a file that will serve as the entry point for our application. This will tell our Gunicorn server how to interact with the application.

Let’s call the file wsgi.py:
```
from app import flask_app

if __name__ == "__main__":
    flask_app.run()
```
## Configuring Gunicorn

Check that Gunicorn can serve the application correctly.
```
cd ~/slackapp
gunicorn --bind 0.0.0.0:3000 wsgi:flask_app
```

Next, let’s create the systemd service unit file. Creating a systemd unit file will allow Ubuntu’s init system to automatically start Gunicorn and serve the Flask application whenever the server boots.

Create a unit file ending in `.service` within the /etc/systemd/system directory to begin:
```
# /etc/systemd/system/slackserver.service
[Unit]
Description=Gunicorn instance to serve slackapp
After=network.target
[Service]
User=caxe
Group=www-data
WorkingDirectory=/home/caxe/slackapp
Environment="PATH=/home/caxe/slackapp/venv/bin"
ExecStart=/home/caxe/slackapp/venv/bin/gunicorn --workers 3 --bind unix:slackapp.sock -m 007 wsgi:flask_app
#  We’ll set an umask value of 007 so that the socket file is created giving access to the owner and group, while restricting other access
[Install]
WantedBy=multi-user.target
```
sudo systemctl start slackapp
sudo systemctl enable slackapp
sudo systemctl status slackapp
## Configuring Nginx to Proxy Requests
Let’s now configure Nginx to pass web requests to that socket by making some small additions to its configuration file.

Begin by creating a new server block configuration file in Nginx’s sites-available directory. Let’s call this slackapp to keep in line with the rest of the guide:
```
# /etc/nginx/sites-available/slackapp
server {
    listen 80;
    server_name your_domain www.your_domain;
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/caxe/slackapp/slackapp.sock;
    }
}
```
To enable the Nginx server block configuration you’ve just created, link the file to the sites-enabled directory:
```
sudo ln -s /etc/nginx/sites-available/slackapp /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
Finally, let’s adjust the firewall again. We no longer need access through port 3000, so we can remove that rule. We can then allow full access to the Nginx server:
```
sudo ufw delete allow 3000
sudo ufw allow 'Nginx Full'
```
>If you encounter any errors, trying checking the following:
>```
>sudo less /var/log/nginx/error.log: checks the Nginx error logs.
>sudo less /var/log/nginx/access.log: checks the Nginx access logs.
>sudo journalctl -u nginx: checks the Nginx process logs.
>sudo journalctl -u slackapp: checks your Flask app’s Gunicorn logs.
## Securing the Application
To ensure that traffic to your server remains secure, get the SSL certificate for your domain.

We will assume the following things:
- The private key, SSL certificate, and, if applicable, the CA’s intermediate certificates are located in a home directory at /home/caxe
- The private key is called example.com.key
- The SSL certificate is called example.com.crt
- The CA intermediate certificate(s) are in a file called intermediate.crt
- If you have a firewall enabled, be sure that it allows port 443 (HTTPS)
> Note: In a real environment, these files should be stored somewhere that only the user that runs the web server master process (usually root) can access. The private key should be kept secure.

With Nginx, if your CA included an intermediate certificate, you must create a single “chained” certificate file that contains your certificate and the CA’s intermediate certificates.

- Change to the directory that contains your private key, certificate, and the CA intermediate certificates (in the intermediate.crt file). We will assume that they are in your home directory for the example:

```
cd ~
cat example.com.crt intermediate.crt > example.com.chained.crt
cd /etc/nginx/sites-enabled
sudo vi default
# Find and modify the following fields
    listen 443 ssl;
    server_name example.com;
    ssl_certificate /home/caxe/example.com.chained.crt;
    ssl_certificate_key /home/caxe/example.com.key;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';
```
If you want HTTP traffic to redirect to HTTPS, you can add this additional server block at the top of the file (replace the highlighted parts with your own information):
```
server {
    listen 80;
    server_name example.com;
    rewrite ^/(.*) https://example.com/$1 permanent;
}
```
Now restart Nginx to load the new configuration and enable TLS/SSL over HTTPS!

    sudo service nginx restart