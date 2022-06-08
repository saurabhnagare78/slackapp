import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import datetime
import json

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
USER_TOKEN = os.environ.get("SLACK_USER_TOKEN")

def pprint(response):
    print(json.dumps(response,indent=4))

# message is an event handler refer: https://api.slack.com/events
@app.event("message") 
def respond(event, say, context, client, body ):
    sender = event["user"]
    receiver = body["authorizations"][0]["user_id"]

    # add event if status set to out of office set presence as away
    user_presence = app.client.users_getPresence(user = receiver)["presence"]
    user_info = app.client.users_info(user = receiver)["user"]

    if (user_presence == "away") and (user_info["profile"]["status_text"]== "Out of Office") and (not sender == receiver):
        expiration = user_info["profile"]["status_expiration"]
        dt = datetime.datetime.fromtimestamp(expiration)
        text = f"Hi, <@{ sender }>!!!\nI am Out of Office and will be back on {dt}"
        app.client.chat_postMessage(
            # response from Bot
            # token = client.token, 
            # username = user_info["name"],
            # icon_url = user_info["profile"]["image_24"],
            token = USER_TOKEN,
            channel = sender,
            text = text,
        )

@app.event("user_status_changed")
def handle_user_status_changed_events(body, logger, event):
    # user = event["user"]["id"]
    status = event["user"]["profile"]["status_text"]
    # If status changed to OOO set presence as inactive
    try:
        if status == "Out of Office":
            print(app.client.users_setPresence(token = USER_TOKEN,presence = "away"))
    except Exception as err:
        print(err)
    # print(json.dumps(body, indent = 4))


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()