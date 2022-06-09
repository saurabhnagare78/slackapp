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

# Issue and consume state parameter value on the server-side.
state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")
# Persist installation data and lookup it by IDs.
installation_store = FileInstallationStore(base_dir="./data")

oauth_settings = OAuthSettings(
    client_id=configur.get("config2","SLACK_CLIENT_ID"),
    client_secret=configur.get("config2","SLACK_CLIENT_SECRET"),
    scopes=["chat:write.customize", "chat:write"],
    user_scopes=["im:history", "im:read", "users:read", "users:write","chat:write"],
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states")
)


installations = [
    {
      "team_id": "T032711JHNH",
      "user_token": configur.get("config2","SLACK_USER_TOKEN"),
      "user_id": "U0329TN5Y5Q",
    },
]

def authorize(enterprise_id, team_id, logger):
    # You can implement your own logic to fetch token here
    for team in installations:
        # enterprise_id doesn't exist for some teams
        is_valid_enterprise = True if (("enterprise_id" not in team) or (enterprise_id == team["enterprise_id"])) else False
        if ((is_valid_enterprise == True) and (team["team_id"] == team_id)):
            # Return an instance of AuthorizeResult
            # If you don't store bot_id and bot_user_id, could also call `from_auth_test_response` with your bot_token to automatically fetch them
            return AuthorizeResult(
              enterprise_id=enterprise_id,
              team_id=team_id,
              user_token=team["user_token"],
              user_id=team["user_id"],
            )

# Initializes your app with your bot token and socket mode handler
app = App(
    signing_secret=configur.get("config2","SLACK_SIGNING_SECRET"),
    # authorize = authorize,
    oauth_settings=oauth_settings
)
# USER_TOKEN = configur.get("config2","SLACK_USER_TOKEN")

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
        # message last read by receiver
        print('Yea')
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
            print('Not Replied')
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
                    token = USER_TOKEN,
                    channel = receiver,
                    text = text,
                )
            except Exception as err:
                print(err)
        else:
            pass
            # print("Already Replied")

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
    # Socket Mode
    # SocketModeHandler(app, configur.get("config2","SLACK_APP_TOKEN")).start()
    # HTTP Mode
    app.start(port=int(os.environ.get("PORT", 3000)))
