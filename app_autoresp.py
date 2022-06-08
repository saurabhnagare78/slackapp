import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import datetime

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
USER_TOKEN = os.environ.get("SLACK_USER_TOKEN")

# message is an event handler refer: https://api.slack.com/events
@app.event("message") 
def respond(event, say, context, client, body ):
    sender = event["user"]
    receiver = body["authorizations"][0]["user_id"]
    # add event if status set to out of office set presence as away
    user_presence = app.client.users_getPresence(user = receiver)["presence"]
    user_info = app.client.users_info(user = receiver)["user"]
    if (user_presence == "away") and (user_info["profile"]["status_text"]== "Out of Office") and (not sender == receiver):
        # message last read by receiver
        last_read = app.client.conversations_info(
            token = USER_TOKEN, 
            channel = event["channel"]
        )["channel"]["last_read"]
        
        # check whether we have already replied in the current date. skip if yes
        # after 20 texts reply again to remind we are out of office

        message_list = app.client.conversations_history(
            token = USER_TOKEN, 
            channel = event["channel"], 
            oldest = last_read, 
            limit = 20
        )["messages"]

        replied = False
        for message in reversed(message_list):
            if "Out of Office" in message["text"]:
                replied = True
                break

        if not replied:
            expiration = user_info["profile"]["status_expiration"]
            if not expiration == 0:
                dt = datetime.datetime.fromtimestamp(expiration)
                text = f"Hi, <@{ sender }>!!!\nI am Out of Office and will be back on {dt}"
            else:
                # add career manager instead of U032ATMNLVC or any other profile field that may exist.
                text = f"Hi, <@{ sender }>!!!\nI'll be Out of Office for a while.\nIn case of emergency please reach out to <@U032ATMNLVC>.\nThanks"
            try:
                app.client.chat_postMessage(
                    # response from Bot
                    # token = client.token, 
                    # username = user_info["name"],
                    # icon_url = user_info["profile"]["image_24"],
                    token = USER_TOKEN,
                    channel = sender,
                    text = text,
                )
            except Exception as err:
                print(err)
        else:
            pass
            # print("Already Replied")

# When selecting Out of Office, change presence to away
@app.event("user_status_changed")
def handle_user_status_changed_events(body, logger, event):
    status = event["user"]["profile"]["status_text"]
    try:
        if status == "Out of Office":
            print(app.client.users_setPresence(token = USER_TOKEN,presence = "away"))
    except Exception as err:
        print(err)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()