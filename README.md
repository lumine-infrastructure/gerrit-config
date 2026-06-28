# lumine-gerrit-config

Gerrit configuration and project management for LumineDroid.

## Structure

- `structure.yml` — list of all Gerrit projects and their parents
- `lib.py` — wrapper for Gerrit API and GitHub API
- `update.py` — main script to sync projects between `structure.yml`, Gerrit, and GitHub

## Usage

Set environment variables:

```bash
export GERRIT_USER=your_gerrit_username
export GERRIT_PASS=your_gerrit_http_password
export ADMIN_GITHUB_TOKEN=your_github_token
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python update.py
```

## Adding a new project

Edit `structure.yml` and add the new project under the appropriate parent:

```yaml
LumineDroid:
  - LumineDroid/new_repo_name
```

Run `update.py` to automatically:
1. Create the project in Gerrit
2. Create the repo on GitHub
3. Set the correct parent in Gerrit
