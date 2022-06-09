from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
installation_store = FileInstallationStore(base_dir="./data")
installation = Installation(
                app_id="ASdsadsad",
                enterprise_id="asdsadsa",
                enterprise_name=None,
                enterprise_url=None,
                team_id="T032711JHNH",
                team_name="sadsdasd",
                bot_token=None,
                bot_id=None,
                bot_user_id=None,
                bot_scopes=None,  # comma-separated string
                user_id="U0329TN5Y5as",
                user_token="asda",
                is_enterprise_install=False,
            )
installation_store.save(installation)

x = installation_store.find_installation(enterprise_id=None,user_id="U0329TN5Y5as",team_id="T032711JHNH")
print(x.user_token)