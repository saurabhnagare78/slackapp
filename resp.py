messages = [
    {
        'bot_id': 'B03JJ9QH1JN', 
        'type': 'message', 
        'text': "Hi, <@U033C7RBM32>!!!\nI'll be Out of Office for a while.\nIn case of emergency please reach out to <@U032ATMNLVC>.\nThanks", 
        'user': 'U0329TN5Y5Q', 
        'ts': '1654671984.380459', 
        'app_id': 'A03JBKWQB7Y', 
        'team': 'T032711JHNH', 
        'bot_profile': {'id': 'B03JJ9QH1JN', 'deleted': False, 'name': 'New App', 'updated': 1654577936, 'app_id': 'A03JBKWQB7Y', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'team_id': 'T032711JHNH'}, 
        'blocks': [{'type': 'rich_text', 'block_id': '1Q3NL', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'Hi, '}, {'type': 'user', 'user_id': 'U033C7RBM32'}, {'type': 'text', 'text': "!!!\nI'll be Out of Office for a while.\nIn case of emergency please reach out to "}, {'type': 'user', 'user_id': 'U032ATMNLVC'}, {'type': 'text', 'text': '.\nThanks'}]}]}]
    }, 
    {
        'client_msg_id': '5cfafdfd-503e-496f-9a0e-fbba67404604', 'type': 'message', 'text': 'QWER', 'user': 'U033C7RBM32', 'ts': '1654671977.943529', 'team': 'T032711JHNH', 'blocks': [{'type': 'rich_text', 'block_id': 'LFv', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'QWER'}]}]}]
    }
]
for message in messages:
    if "Out of Office" in message["text"]:
        print('yes')
        break
