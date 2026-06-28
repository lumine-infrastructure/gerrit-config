import yaml
import requests
from github import Github, Auth
from lib import Gerrit, Config

gerrit = Gerrit()
github = Github(auth=Auth.Token(Config.GITHUB_TOKEN))

with open("structure.yml", "r") as f:
    wanted = yaml.load(f.read(), Loader=yaml.BaseLoader)

live = gerrit.get_projects()

print("Creating gerrit repos...")
missing = set()
for parent, children in wanted.items():
    if parent not in live.keys():
        missing.add(parent)
    for child in children:
        if child not in live.keys():
            missing.add(child)

if missing:
    print(f"Missing projects: {missing}")
    # Create parents first, then children
    parents = [p for p in missing if p in wanted.keys()]
    children_list = [p for p in missing if p not in wanted.keys()]
    for project in parents + children_list:
        print(f"Creating {project} on gerrit...")
        parent_name = None
        for p, ch in wanted.items():
            if project in ch:
                parent_name = p
                break
        gerrit.create_project(project, parent=parent_name)

print("Creating github repos...")
for org_name in ["LumineDroid", "LumineDroid-Devices"]:
    try:
        org = github.get_organization(org_name)
        github_projects = {f"{org_name}/{x.name}" for x in org.get_repos()}
        gerrit_projects = set()

        for parent, children in wanted.items():
            if parent.startswith(f"{org_name}/"):
                gerrit_projects.add(parent)
            for child in children:
                if child.startswith(f"{org_name}/"):
                    gerrit_projects.add(child)

        missing_gh = gerrit_projects - github_projects
        for repo in missing_gh:
            repo_name = repo.split("/", 1)[1]
            print(f"Creating {repo} on github...")
            new_repo = org.create_repo(
                repo_name,
                has_wiki=False,
                has_downloads=False,
                has_projects=False,
                has_issues=False,
                private=False,
            )
    except Exception as e:
        print(f"Skipping org {org_name}: {e}")

print("Updating gerrit permissions...")
for parent, children in wanted.items():
    for child in children:
        if live.get(child, {}).get("parent") != parent:
            print(f"Setting parent of {child} to {parent}")
            gerrit.update_parent(child, parent)

print("Done!")
