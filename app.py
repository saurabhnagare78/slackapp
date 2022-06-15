import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
from requests.auth import HTTPBasicAuth
from configparser import ConfigParser
# Initializes your app with your bot token and socket mode handler

configur = ConfigParser()
configur.read('config.ini')

app = App(token=configur.get("config","SLACK_BOT_TOKEN"))
JIRA_TOKEN = configur.get("jira","JIRA_TOKEN")
JIRA_URL = configur.get("jira","JIRA_URL")
JIRA_USERNAME = configur.get("jira","JIRA_USERNAME")

data = {}
with open('departments.txt', 'r') as fp:
    depts = fp.read().splitlines() # ['H.R', 'I.T', 'Accounts']
for dept in depts:
    data[dept] = ''
for file_name in depts:
    with open(f'{file_name}_categories.txt', 'r') as fp:
        catgs = fp.read().splitlines()
        data[file_name] = catgs # {'H.R': ['Leaves', 'Holidays', 'Background Verification'], 'I.T': ['Software Install', 'Network Access', 'Locked Out'], 'Accounts': ['Payslips', 'Form 16', 'PF Withdrawal']}

options_1 = []
for option in depts:
    options_1.append(
        {
            "text": {
                "type": "plain_text",
                "text": option,
                "emoji": True
            },
            "value": f"dept_{option}"
        } 
    )

def app_description_block()
    data  = {
                    "type": "section",
                    "block_id": "app_description",
                    "text": {
                        "type": "plain_text",
                        "text": "Your Personal Help Desk",
                        "emoji": True
                    }
                }
    return data

def dept_selection_block(text1, text2):
    global options_1
    data = {
            "type": "section",
            "block_id": "dept_selection",
            "text": {
                "type": "mrkdwn",
                "text": text1
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": text2,
                    "emoji": True
                },
                "options": options_1,
                "action_id": "dept_selection"
            }
        }
    return data

def dept_category_selection_block(text1, text2)
    global options_2
    data = {
        "type": "section",
        "block_id": "dept_category_selection",
        "text": {
            "type": "mrkdwn",
            "text": text1
        },
        "accessory": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": text2,
                "emoji": True
            },
            "options": options_2,
            "action_id": "dept_category_selection"
        }
    }
    return data

# First Page
@app.shortcut("caxe_app_shortcut")
def open_modal(ack, shortcut, client):
    # Acknowledge the shortcut request
    ack()
    # Call the views_open method using the built-in WebClient
    client.views_open(
        trigger_id=shortcut["trigger_id"],
        # A simple view payload for a modal
        view={
            "type": "modal",
            "callback_id": "dept_selection_view",
            "title": {"type": "plain_text", "text": "Stealth Mode"},
            "close": {"type": "plain_text", "text": "Close"},
            # "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                app_description_block(),
                dept_selection_block("Select the Relevant Department", "Select an item")
            ]
        }
    )
# Second Page
@app.action("dept_selection")
def update_modal(ack, body, client):
    ack()
    global options_2
    options_2 = []
    for option in data[body['actions'][0]['selected_option']['text']['text']]:
        options_2.append(
            {
                "text": {
                    "type": "plain_text",
                    "text": option,
                    "emoji": True
                },
                "value": f"hr_category_{option}"
            }
        )
    client.views_update(
        # Pass the view_id
        view_id=body["view"]["id"],
        # String that represents view state to protect against race conditions
        hash=body["view"]["hash"],
        # View payload with updated blocks
        view={
            "type": "modal",
            # View identifier
            "callback_id": "dept_category_selection",
            "title": {"type": "plain_text", "text": "Updated modal"},
            "blocks": [
                app_description_block(),
                dept_selection_block(
                    "Selected Department", 
                    f"{ body['actions'][0]['selected_option']['text']['text']}"
                ),
                dept_category_selection_block(
                    "Select the Issue Category",
                    "Select an item"
                ),
            ]
        }
    )

# Third Page
@app.action("dept_category_selection")
def update_modal(ack, body, client):
    ack()
    client.views_update(
        # Pass the view_id
        view_id=body["view"]["id"],
        # String that represents view state to protect against race conditions
        hash=body["view"]["hash"],
        # View payload with updated blocks
        view={
            "type": "modal",
            # View identifier
            "callback_id": "create_ticket",
            "title": {"type": "plain_text", "text": "Updated modal"},
            "close": {"type": "plain_text", "text": "Close"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                app_description_block(),
                dept_selection_block(
                    "Selected Department",
                    f"{ body['view']['blocks'][1]['accessory']['placeholder']['text']}"
                ),
                dept_category_selection_block(
                    "Selected Issue Category",
                    f"{ body['actions'][0]['selected_option']['text']['text'] }"
                ),
                {
                    "type": "input",
                    "block_id": "issue_description",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "plain_text_input-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Describe your Issue",
                        "emoji": True
                    }
                }
            ]
        }
    )


@app.view("create_ticket")
def action_button_click(body, ack, say, view):
    # Acknowledge the action
    ack()
    # hopes_and_dreams = view["state"]["values"]["input_c"]["dreamy_input"]
    print('Creating Ticket')

    ticket_data = {
        "fields": {
            "project": {
                "key": "TEST"
            },
            "summary": f"{body['view']['state']['values']['dept_category_selection']['dept_category_selection']['selected_option']['text']['text']}",
            "description": f"Issue created by: <@{body['user']['id']}>\nhttps://{body['team']['domain']}.slack.com/team/{body['user']['id']}\nDetails:\n{ body['view']['state']['values']['issue_description']['plain_text_input-action']['value'] }",
            "issuetype": {
                "name": "Task"
            }
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        resp = requests.post(
            url= JIRA_URL, 
            json = ticket_data,
            headers = headers,
            auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_TOKEN)
            )
    except Exception as e:
        print(e)

    print(f"Ticket Created Successfully!")
    say(
        text = f"Ticket Created Successfully with reference id {resp.json()['key'] + ': ' + resp.json()['id']}!",
        channel = body['user']['id']    
    )

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, configur.get("config","SLACK_APP_TOKEN")).start()