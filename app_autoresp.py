import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import datetime

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
@app.event("message") # message is an event handler refer: https://api.slack.com/events
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
            token = client.token, 
            channel = sender,
            text = text,
            username = user_info["name"],
            icon_url = user_info["profile"]["image_24"],
        )

@app.event("user_status_changed")
def handle_user_status_changed_events(body, logger):
    print(body)
    # If status changed to OOO set presence as inactive


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()