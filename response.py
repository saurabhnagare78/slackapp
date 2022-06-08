{
    'type': 'view_submission', 
    'team': {'id': 'T032711JHNH', 'domain': 'slackjiratest-group'}, 
    'user': {'id': 'U033C7RBM32', 'username': 'faizan.qazi', 'name': 'faizan.qazi', 'team_id': 'T032711JHNH'}, 
    'api_app_id': 'A032X2HRMGT', 'token': '1PD6q1ECt2ADG1nK4JormDd3', 'trigger_id': '3099145060310.3075035629765.abe546d0d1a3954468121746f51d02e2', 
    'view': {
        'id': 'V032X47JNS2', 
        'team_id': 'T032711JHNH', 
        'type': 'modal', 
        'blocks': [
            {'type': 'section', 'block_id': 'app_description', 'text': {'type': 'plain_text', 'text': 'Your Personal Help Desk', 'emoji': True}}, 
            {'type': 'section', 'block_id': 'dept_selection', 'text': {'type': 'mrkdwn', 'text': 'Selected Department', 'verbatim': False}, 'accessory': {'type': 'static_select', 'action_id': 'dept_selection', 'placeholder': {'type': 'plain_text', 'text': 'H.R', 'emoji': True}, 'options': [{'text': {'type': 'plain_text', 'text': 'H.R', 'emoji': True}, 'value': 'dept_hr'}, {'text': {'type': 'plain_text', 'text': 'I.T', 'emoji': True}, 'value': 'dept_it'}, {'text': {'type': 'plain_text', 'text': 'Accounts', 'emoji': True}, 'value': 'dept_acc'}]}
            }, 
            {'type': 'section', 'block_id': 'dept_category_selection', 'text': {'type': 'mrkdwn', 'text': 'Selected Issue Category ', 'verbatim': False}, 'accessory': {'type': 'static_select', 'action_id': 'dept_category_selection', 'placeholder': {'type': 'plain_text', 'text': 'HR 1', 'emoji': True}, 'options': [{'text': {'type': 'plain_text', 'text': 'HR 0', 'emoji': True}, 'value': 'hr_category_0'}, {'text': {'type': 'plain_text', 'text': 'HR 1', 'emoji': True}, 'value': 'hr_category_1'}, {'text': {'type': 'plain_text', 'text': 'HR 2', 'emoji': True}, 'value': 'hr_category_2'}]}}, 
            {'type': 'input', 'block_id': 'issue_description', 'label': {'type': 'plain_text', 'text': 'Describe your Issue', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'plain_text_input', 'action_id': 'plain_text_input-action', 'multiline': True, 'dispatch_action_config': {'trigger_actions_on': ['on_enter_pressed']}}}
        ], 
        'private_metadata': '', 
        'callback_id': 'create_ticket', 
        'state': {'values': {'dept_selection': {'dept_selection': {'type': 'static_select', 'selected_option': {'text': {'type': 'plain_text', 'text': 'H.R', 'emoji': True}, 'value': 'dept_hr'}}}, 'dept_category_selection': {'dept_category_selection': {'type': 'static_select', 'selected_option': {'text': {'type': 'plain_text', 'text': 'HR 1', 'emoji': True}, 'value': 'hr_category_1'}}}, 'issue_description': {'plain_text_input-action': {'type': 'plain_text_input', 'value': 'I want everything to be displayed'}}}}, 'hash': '1644914730.hmagsKpD', 'title': {'type': 'plain_text', 'text': 'Updated modal', 'emoji': True}, 'clear_on_close': False, 'notify_on_close': False, 'close': {'type': 'plain_text', 'text': 'Close', 'emoji': True}, 'submit': {'type': 'plain_text', 'text': 'Submit', 'emoji': True}, 'previous_view_id': None, 'root_view_id': 'V032X47JNS2', 'app_id': 'A032X2HRMGT', 'external_id': '', 'app_installed_team_id': 'T032711JHNH', 'bot_id': 'B032X279UGJ'}, 'response_urls': [], 'is_enterprise_install': False, 'enterprise': None}