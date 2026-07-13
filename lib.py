import functools
import json
import os
import textwrap
import time
from urllib.parse import quote_plus

import requests
from requests import auth as rauth


class Config:
    GERRIT_USER = os.environ.get("GERRIT_USER", "")
    GERRIT_PASS = os.environ.get("GERRIT_PASS", "")
    GITHUB_TOKEN = os.environ.get("ADMIN_GITHUB_TOKEN", "")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


class Gerrit:
    GERRIT_OFFLINE_MESSAGE = textwrap.dedent("""
        <pre>
        Hello! If you're seeing this, gerrit is offline for some reason or another. It should be back soon!
        </pre>
    """).strip()

    def __init__(self):
        self.auth = rauth.HTTPBasicAuth(Config.GERRIT_USER, Config.GERRIT_PASS)
        self.base_url = "https://review.luminedroid.org"

    def _retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if Gerrit.GERRIT_OFFLINE_MESSAGE in str(e):
                    print("Gerrit is offline, waiting 5 minutes before retrying...")
                    time.sleep(60 * 5)
                    return func(*args, **kwargs)
                raise
        return wrapper

    @_retry
    def get_projects(self):
        url = f"{self.base_url}/a/projects/?t"
        resp = requests.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise Exception(f"Error communicating with gerrit: {resp.text}")
        projects = json.loads(resp.text[5:])
        return projects

    @_retry
    def update_parent(self, child, parent):
        child_encoded = quote_plus(child)
        url = f"{self.base_url}/a/projects/{child_encoded}/parent"
        print(f"Updating {child}'s parent to {parent}")
        resp = requests.put(url, json={"parent": parent, "commit_message": "Auto update from gerrit_config"}, auth=self.auth)
        if resp.status_code != 200:
            raise Exception(f"Error communicating with gerrit: {resp.text}")

    @_retry
    def replace_project_permissions(self, project: str, permissions: dict) -> bool:
        url = f"{self.base_url}/a/projects/{quote_plus(project)}/access"
        resp = requests.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise Exception(f"Error fetching permissions from gerrit: code {resp.status_code}, response: {resp.text}")

        perms = self._decode_raw(resp.text).get("local", {})
        if perms != permissions:
            if perms:
                resp = requests.post(f"{self.base_url}/a/projects/{quote_plus(project)}/access", auth=self.auth, json={"remove": perms})
                if resp.status_code != 200:
                    raise Exception(f"Error removing gerrit permissions: {resp.text}")
            resp = requests.post(f"{self.base_url}/a/projects/{quote_plus(project)}/access", auth=self.auth, json={"add": permissions})
            if resp.status_code != 200:
                raise Exception(f"Error setting gerrit permissions: {resp.text}")
            return True
        return False

    def create_project(self, name, parent=None):
        url = f"{self.base_url}/a/projects/{name.replace('/', '%2F')}"
        body = {}
        if parent:
            body["parent"] = parent
        resp = requests.put(url, auth=self.auth, json=body)
        if resp.status_code not in (200, 201):
            raise Exception(f"Error communicating with gerrit: {resp.text}")

    @_retry
    def get_groups(self):
        url = f"{self.base_url}/a/groups/"
        resp = requests.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise Exception(f"Error communicating with gerrit: {resp.text}")
        groups = json.loads(resp.text[5:])
        return groups

    @_retry
    def create_group(self, name):
        url = f"{self.base_url}/a/groups/{quote_plus(name)}"
        data = {"visible_to_all": True}
        resp = requests.put(url, auth=self.auth, json=data)
        if resp.status_code not in (200, 201):
            raise Exception(f"Error communicating with gerrit: {resp.text}")

    def _decode_raw(self, input: str):
        return json.loads(input[5:])


def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": Config.TELEGRAM_CHAT_ID, "text": text})
    if resp.status_code != 200:
        raise Exception(f"Error sending telegram message: {resp.text}")
