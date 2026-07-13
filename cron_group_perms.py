from datadiff import diff

from lib import Gerrit, send_telegram_message

gerrit = Gerrit()

projects = [x for x in gerrit.get_projects() if any([x.startswith("PROJECT-"), x.startswith("OEM-")])]

groups = gerrit.get_groups()
modified = []
for project in projects:
    group_data = groups.get(project, None)
    if not group_data:
        print(f"Missing group for {project} - creating")
        gerrit.create_group(project)
        continue
    group = str(group_data["id"])
    branches = [
        "refs/heads/staging/*",
        "refs/heads/backup/*",
        "refs/heads/bellflower",
        "refs/heads/camellia",
    ]
    new = {
        'refs/heads/*': { 'permissions': {
            'label-Code-Review': {
                'rules': { group: {
                    'action': 'ALLOW',
                    'force': False,
                    'max': 2,
                    'min': -2,
              }},
              'label': 'Code-Review'
            },
           'label-Verified': {
               'rules': { group: {
                   'action': 'ALLOW',
                   'force': False,
                   'max': 1,
                   'min': -1,
             }},
             'label': 'Verified'
           },
            'submit': {
                'rules': { group: {
                    'action': 'ALLOW',
                    'force': False
                }}
            },
            'forgeAuthor': {
                'rules': { group: {
                    'action': 'ALLOW',
                    'force': False
                }}
            },
            'push': {
                'rules': { group: {
                    'action': 'ALLOW',
                    'force': False
                }}
            },
            'pushMerge': {
                'rules': { group: {
                    'action': 'ALLOW',
                    'force': False
                }}
            },
            'forgeCommitter': {
                'rules': { group: {
                    'action': 'ALLOW',
                    'force': False
                }}
            },
            'forgeServerAsCommitter': {
                'rules': { group: {
                    'action': 'ALLOW',
                    'force': False
                }}
            },
            'abandon': {
                'rules': {group: {
                    'action': 'ALLOW',
                    'force': False
                }}
            },
            'editTopicName': {
                'rules': {group: {
                    'action': 'ALLOW',
                    'force': False
                }}
            },
        }},
    }

    for branch in branches:
        new[branch] = {
            'permissions': {
                'create': {
                    'rules': {group: {
                        'action': 'ALLOW',
                        'force': False
                    }}
                },
            }
        }
    updated = gerrit.replace_project_permissions(project, new)
    if updated:
         modified.append(project)

if modified:
    send_telegram_message(f"Reset project permissions on {', '.join(modified)}")
