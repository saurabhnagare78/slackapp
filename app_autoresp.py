import os
import datetime
from configparser import ConfigParser
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.authorization import AuthorizeResult
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_bolt.oauth.oauth_settings import OAuthSettings

configur = ConfigParser()
configur.read('config.ini')

oauth_settings = OAuthSettings(
    client_id=configur.get("config2","SLACK_CLIENT_ID"),
    client_secret=configur.get("config2","SLACK_CLIENT_SECRET"),
    scopes=["chat:write.customize", "chat:write"],
    user_scopes=["im:history", "im:read", "users:read", "users:write","chat:write"],
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states")
)

# Initializes your app with your bot token and socket mode handler
app = App(
    signing_secret=configur.get("config2","SLACK_SIGNING_SECRET"),
    oauth_settings=oauth_settings
)

# message is an event handler refer: https://api.slack.com/events ; 
@app.event("message") 
def respond(event, say, context, client, body ):
    USER_TOKEN = context.user_token #sender
    sender = event["user"]
    receiver = body["authorizations"][0]["user_id"]
    # for info on methods: https://api.slack.com/methods
    user_presence = app.client.users_getPresence(
        user = receiver, 
        token = USER_TOKEN
    )["presence"]
    user_info = app.client.users_info(
        user = receiver,
        token = USER_TOKEN
    )["user"]
    if (user_presence == "away") and (user_info["profile"]["status_text"]== "Out of Office") and (not sender == receiver):
        try:
            installation_store = FileInstallationStore(base_dir="./data/installations")
            x = installation_store.find_installation(
                enterprise_id = user_info.get("enterprise_id",None),
                team_id = user_info["team_id"],
                user_id = user_info["id"],
                is_enterprise_install = user_info.get("is_enterprise_install",False),
            )
            RECEIVER_TOKEN = x.user_token
        except:
            print('failed to fetch user token')
        # message last read by receiver
        last_read = app.client.conversations_info(
            token = RECEIVER_TOKEN, 
            channel = event["channel"]
        )["channel"]["last_read"]
        
        # check whether we have already replied in the current date. skip if yes
        # after 20 texts reply again to remind we are out of office

        message_list = app.client.conversations_history(
            token = RECEIVER_TOKEN, 
            channel = event["channel"], 
            oldest = last_read, 
        )["messages"]
        replied = False
        for idx, message in enumerate(message_list):
            # reply for every 20 Unresponded texts
            if idx == 19:
                break
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
                    # respond with Bot
                    # token = client.token, 
                    # username = user_info["name"],
                    # icon_url = user_info["profile"]["image_24"],
                    token = RECEIVER_TOKEN,
                    channel = sender,
                    text = text,
                )
            except Exception as err:
                print(err)
        else:
            print("Already Replied")
            pass

# When selecting Out of Office, change presence to away
@app.event("user_status_changed")
def handle_user_status_changed_events(logger, event, context):
    status = event["user"]["profile"]["status_text"]
    try:
        if status == "Out of Office":
            app.client.users_setPresence(
                token = context.user_token,
                presence = "away"
                )
    except Exception as err:
        print(err)


# Start your app
if __name__ == "__main__":
    ## Socket Mode
    # SocketModeHandler(app, configur.get("config2","SLACK_APP_TOKEN")).start()
    ## HTTP Mode
    app.start(port=int(os.environ.get("PORT", 3000)))
