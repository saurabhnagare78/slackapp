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

######################################################################################
######################################################################################



def create_field(text, value):
    '''
    Creates the options in the required format
    '''
    data = {
        "text": {
            "type": "plain_text",
            "text": text,
        },
        "value": value
    }
    return data

def create_initial_options(body,block_name,block_action):
    return create_field(
        body['view']['state']['values'][block_name][block_action]['selected_option']['text']['text'],
        body['view']['state']['values'][block_name][block_action]['selected_option']['value']
    )

def create_options(vals_list):
    '''
    Creates the options in the required format 
    Accepts List of tuple including name,value
    '''
    options = []
    for val in vals_list:
        options.append(
            {
                "text": {
                    "type": "plain_text",
                    "text": f"{val[0]}",
                },
                "value": val[1]
            }
        )
    return options
master_data = {}
def generate_master_dict():
    '''
    Generates the departments list with their categories for use as options from file `departments.txt`
    '''
    global master_data
    master_data = {}
    with open('departments.txt','r') as fp:
        departments = fp.read().splitlines()
    for dept_name in departments:
        master_data[dept_name] = {
            'name': create_field(dept_name, f'dept_{dept_name}'),
            'categories': []
        }
        with open(f'{dept_name}_categories.txt','r') as fp:
            categories = fp.read().splitlines()
        for category in categories:
            master_data[dept_name]['categories'].append(create_field(category, f'{dept_name}_category_{category}'))
    print('Master Data\n',master_data)
    print('*'*150)
generate_master_dict()
# blocks with action_id calls `@app.action` decorator with the defined name
# eg. "action_id": 'demo_action' will execute @app.action('demo_action')
def create_block(text1, options = None, action = None, initial_option = None, text2 = None, type1 = None, block_id = None, type2 = 'section'):
    '''
    To generate block, 
    type ->
        For Dropdown send `static_select`
        For Radio send `radio_buttons`
    `initial_option` -> set the default option. -> {
        'value': 'value1',
        'text': 'dummy_text'
    }
    Options -> The options you want to display
    action -> the function to call on user interaction with this block
    '''
    # Block Pre Meta
    if type2 == 'section':
        elem_or_acc = 'accessory'
        text_or_labl = 'text'
    else:
        elem_or_acc = 'element'
        text_or_labl = 'label'
    data={
        'type': type2,
        text_or_labl: {
            'type': "plain_text",
            'text': text1
        }
    }
    if type1:
        data[elem_or_acc] =  {
            'type': type1,
            'options': options,
            'action_id': action,
        }
    if initial_option:
        data[elem_or_acc]['initial_option'] = {
            "value": initial_option['value'],
            "text": {
                "type": "plain_text",
                "text": initial_option['text']
            }
        }
    if type1 == 'static_select':
        data[elem_or_acc]['placeholder'] = {
            "type": "plain_text",
            "text": text2,
        }
    if block_id:
        data['block_id'] = block_id
    return data

######################################################################################
######################################################################################

data = {}
with open('departments.txt', 'r') as fp:
    depts = fp.read().splitlines() # ['H.R', 'I.T', 'Accounts']
for dept in depts:
    data[dept] = ''
for file_name in depts:
    with open(f'{file_name}_categories.txt', 'r') as fp:
        catgs = fp.read().splitlines()
        data[file_name] = catgs # {'H.R': ['Leaves', 'Holidays', 'Background Verification'], 'I.T': ['Software Install', 'Network Access', 'Locked Out'], 'Accounts': ['Payslips', 'Form 16', 'PF Withdrawal']}

def departments_list():
    global master_data
    data = []
    for val in master_data.values():
        data.append(val['name'])
    return data

def block_description(block_id, text):
    data = {
        "type": "section",
        "block_id": block_id,
        "text": {
            "type": "mrkdwn",
            "text": text,
        }
    }
    return data

def app_description_block():
    data  = block_description("app_description", "Your Personal Help Desk")
    return data

def drop_accessory_field(text, options, action):
    '''
    dispalys the options in drop down and redirects to specified `app.action()`
    '''
    data = {
        "type": "static_select",
        "placeholder": {
            "type": "plain_text",
            "text": text,
            "emoji": True
        },
        "options": options,
        "action_id": action
    }
    return data


def dept_selection_block2(text1, text2):
    # displays all the departments in a dropdown menu
    global departments_list
    data = {
        "type": "section",
        "block_id": 'input_category',
        "text": {
            "type": "mrkdwn",
            "text": text1,
        }
    }
    data["accessory"] = {
        "type": "static_select",
        "placeholder": {
            "type": "plain_text",
            "text": text2,
            "emoji": True
        },
        "options": departments_list,
        "action_id": 'input_category'
    }
    return data


def dept_selection_block(text1, text2):
    global departments_list
    data = block_description("dept_selection", text1)
    data["accessory"] = drop_accessory_field(text2, departments_list, "dept_selection")
    return data

def dept_category_selection_block(text1, text2):
    # displays all the department's issue categories in a dropdown menu
    global options_2
    data = block_description("dept_category_selection", text1)
    data["accessory"] = drop_accessory_field(text2, options_2, "dept_category_selection")
    return data

@app.shortcut("admin_caxe")
def open_modal(ack, body, logger, shortcut, client):
    ack()
    x = app.client.users_info(
        token = configur.get("config","SLACK_BOT_TOKEN"),
        user = body['user']['id']
    )
    # Check if Admin
    if x['user']['is_owner'] or True:
        client.views_open(
            trigger_id=shortcut["trigger_id"],
            # A simple view payload for a modal
            view={
                "type": "modal",
                "callback_id": "add_dept_view",
                "title": {"type": "plain_text", "text": "Stealth Mode"},
                "close": {"type": "plain_text", "text": "Close"},
                # https://app.slack.com/block-kit-builder
                "blocks": [
                    create_block(
                        '"Hi, Here you can add new departments for Help Desk or Update any existing ones."',
                        block_id = "description_block"
                    ),
                    {
                        "type": "divider",
                        "block_id": "divider_block"
                    },
                    create_block( 
                        "Select",
                        block_id = "add_update_radio_block",
                        options = create_options(
                            [
                                ("Update Existing Department","value-0"),
                                ("Add New Department","value-1")
                            ]
                        ),
                        action = "add_update_radio_buttons_action",
                        type1 = 'radio_buttons'
                    )
                ]
            }
        )
    else:
        client.views_open(
        trigger_id=shortcut["trigger_id"],
        # A simple view payload for a modal
        view={
            "type": "modal",
            "callback_id": "add_dept_view",
            "title": {"type": "plain_text", "text": "Stealth Mode"},
            "close": {"type": "plain_text", "text": "Close"},
            "blocks": [
                create_block('Only Admins are allowed to use this feature!!!')
            ]
        }
        )
@app.action("add_update_radio_buttons_action")
def update_modal(ack, body, client):
    ack()
    print('radio_button_selected_successfully')
    prev_blocks = body['view']['blocks'] # 0 > description, 1 > divider, 2 > radio, 3 > dropdown
    prev_blocks[2]['accessory']['initial_option'] = create_initial_options(body, 'add_update_radio_block', 'add_update_radio_buttons_action')
    prev_blocks.append(create_block(
                        "Select the Relevant Department",
                        text2 = "Select an item",
                        block_id = 'dept_list_drop_down_block',
                        type1 = 'static_select',
                        action = 'dept_drop_down_action',
                        options = departments_list(),
                    ))
    choice = body['actions'][0]['selected_option']['value']
    if choice == 'value-0':
        client.views_update(
            # Pass the view_id
            view_id=body["view"]["id"],
            # String that represents view state to protect against race conditions
            hash=body["view"]["hash"],
            # View payload with updated blocks
            view={
                "type": "modal",
                # View identifier
                "callback_id": "dept_category_selection2",
                "title": {"type": "plain_text", "text": "Updated modal"},
                "blocks": prev_blocks
            }
        )
    elif choice == 'value-1':
        pass

@app.view("update_files")
def handle_view_events(client,ack, body, logger):
    ack()
    print('category_input_submitted_successfully')
    if body['view']['state']['values']['add_delete_category_block']['add_delete_category_action']['selected_option']['value'] == 'del_cat':
        print('Delete Category Pending Call Successful')
        message = 'Category deleted Successfully!!!'
    else:
        catgs = body['view']['state']['values']['enter_category_text_block']['plain_text_input_action']['value']
        catgs = catgs.split(',')
        dept = body['view']['state']['values']['dept_list_drop_down_block']['dept_drop_down_action']['selected_option']['text']['text']
        with open(f'{dept}_categories.txt','a') as fp:
            for cat in catgs:
                if len(cat) > 0:
                    fp.write(cat+'\n')
        message = 'Category added Successfully!!!'
    client.views_open(
        trigger_id=body["trigger_id"],
        # A simple view payload for a modal
        view={
            "type": "modal",
            "callback_id": "add_dept_view",
            "title": {"type": "plain_text", "text": "Stealth Mode"},
            "close": {"type": "plain_text", "text": "Close"},
            "blocks": [
                create_block(message)
            ]
        }
    )

@app.action("plain_text_input_action")
def update_modal(ack, body, client):
    ack()
    print('this')


@app.action("dept_drop_down_action")
def update_modal(ack, body, client):
    ack()
    print('dept_drop_down_action_selected_successfully')
    prev_blocks = body['view']['blocks'] # 0 > description, 1 > divider, 2 > radio, 3 > dropdown
    prev_blocks[2]['accessory']['initial_option'] = create_initial_options(body, 'add_update_radio_block', 'add_update_radio_buttons_action')
    prev_blocks[3]['accessory']['initial_option'] = create_initial_options(body, 'dept_list_drop_down_block', 'dept_drop_down_action')

    prev_blocks.append(
        create_block( 
            "Select",
            block_id = "add_delete_category_block",
            options = create_options(
                [
                    ("Add New Category","add_cat"),
                    ("Delete a Category","del_cat")
                ]
            ),
            action = "add_delete_category_action",
            type1 = 'radio_buttons'
        )
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
            "callback_id": "update_files",
            "title": {"type": "plain_text", "text": "Updated modal"},
            "close": {"type": "plain_text", "text": "Close"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": prev_blocks
        }
    )

@app.action("add_delete_category_action")
def update_modal(ack, body, client):
    ack()
    print('add_delete_category_action_selected_successfully')
    prev_blocks = body['view']['blocks'] # 0 > description, 1 > divider, 2 > radio, 3 > dropdown, 4 > radio 
    prev_blocks[2]['accessory']['initial_option'] = create_initial_options(body, 'add_update_radio_block', 'add_update_radio_buttons_action')
    prev_blocks[3]['accessory']['initial_option'] = create_initial_options(body, 'dept_list_drop_down_block', 'dept_drop_down_action')
    prev_blocks[4]['accessory']['initial_option'] = create_initial_options(body, 'add_delete_category_block', 'add_delete_category_action')
    # check delete or add
    if prev_blocks[4]['accessory']['initial_option']['value'] == 'del_cat':
        prev_blocks.append(
            create_block(
                "Select the category you want to delete",
                text2 = "Category",
                type2 = 'input',
                block_id = 'dept_category_list_drop_down_block',
                type1 = 'static_select',
                action = 'dept_category_list_drop_down_action',
                options = master_data[prev_blocks[3]['accessory']['initial_option']['text']['text']]['categories'],
            )
        )
    else:
        prev_blocks.append(
            {
                "type": "input",
                "block_id": "enter_category_text_block",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "plain_text_input_action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter Categories, separated by commas",
                    "emoji": True
                }
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
            "callback_id": "update_files",
            "title": {"type": "plain_text", "text": "Updated modal"},
            "close": {"type": "plain_text", "text": "Close"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": prev_blocks
        }
    )

@app.action("add_delete_category_action")
def update_modal(ack, body, client):
    ack()
    print('dept_drop_down_action_selected_successfully')
    prev_blocks = body['view']['blocks'] # 0 > description, 1 > divider, 2 > radio, 3 > dropdown, 4 > radio 
    prev_blocks[2]['accessory']['initial_option'] = create_initial_options(body, 'add_update_radio_block', 'add_update_radio_buttons_action')
    prev_blocks[3]['accessory']['initial_option'] = create_initial_options(body, 'dept_list_drop_down_block', 'dept_drop_down_action')
    prev_blocks[4]['accessory']['initial_option'] = create_initial_options(body, 'add_delete_category_block', 'add_delete_category_action')
    prev_blocks.append({
                    "type": "input",
                    "block_id": "enter_category_text_block",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "plain_text_input_action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Enter Categories, separated by commas",
                        "emoji": True
                    }
                })
    client.views_update(
        # Pass the view_id
        view_id=body["view"]["id"],
        # String that represents view state to protect against race conditions
        hash=body["view"]["hash"],
        # View payload with updated blocks
        view={
            "type": "modal",
            # View identifier
            "callback_id": "update_files",
            "title": {"type": "plain_text", "text": "Updated modal"},
            "close": {"type": "plain_text", "text": "Close"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": prev_blocks
        }
    )

# First Page
@app.shortcut("caxe_app_shortcut")
def open_modal(ack, shortcut, client, body, context):
    # Acknowledge the shortcut request
    ack()
    # Call the views_open method using the built-in WebClient https://api.slack.com/reference/surfaces/views
    client.views_open(
        trigger_id=shortcut["trigger_id"],
        # A simple view payload for a modal
        view={
            "type": "modal",
            "callback_id": "dept_selection_view",
            "title": {"type": "plain_text", "text": "Stealth Mode"},
            "close": {"type": "plain_text", "text": "Close"},
            # "submit": {"type": "plain_text", "text": "Submit"},
            # https://app.slack.com/block-kit-builder
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
                        "action_id": "plain_text_input_action"
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
    # https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
    ticket_data = {
        "fields": {
            "project": {
                "key": "TEST" # Same as existing JIRA Project
            },
            "summary": f"{body['view']['state']['values']['dept_category_selection']['dept_category_selection']['selected_option']['text']['text']}",
            "description": f"Issue created by: <@{body['user']['id']}>\nhttps://{body['team']['domain']}.slack.com/team/{body['user']['id']}\nDetails:\n{ body['view']['state']['values']['issue_description']['plain_text_input_action']['value'] }",
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