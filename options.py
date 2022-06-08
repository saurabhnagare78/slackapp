data = {}
with open('departments.txt', 'r') as fp:
    depts = fp.read().splitlines()
for dept in depts:
    data[dept] = ''
for file_name in data.keys():
    with open(f'{file_name}_categories.txt', 'r') as fp:
        catgs = fp.read().splitlines()
        data[file_name] = catgs

options_1 = []
for option in data.keys():
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

options_2 = []
for option in data['H.R']:
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

print(options_1)
