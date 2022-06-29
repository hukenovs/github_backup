## GitHub backup repositories
Save your repos and list of stargazers & list of forks for them. Pure python3 and git with no dependencies to install.

[GitHub API Documentation](https://docs.github.com/en/rest)

| **Title**   | GitHub Backup       |
|:------------|:--------------------|
| **Author**  | [Alexander Kapitanov](https://habr.com/ru/users/hukenovs/) |
| **Sources** | Python3             |
| **Contact** | `<hidden>`          |
| **Release** | 16 Apr 2022         |
| **License** | MIT                 |

### Command line arguments
```bash
usage: backup.py [-h] -u USER_LOGIN [-t USER_TOKEN] [--user_forks] [-v] [-f] \
[--forks] [--stars] [--save | --clone] [--bare] [--recursive] [--starred] [-p SAVE_PATH] \
[-l REPO_LIST [REPO_LIST ...]]

GitHub saver for stargazers, forks, repos.

optional arguments:
  -h, --help            show this help message and exit
  -u USER_LOGIN, --user_login USER_LOGIN
                        User login
  -t USER_TOKEN, --user_token USER_TOKEN
                        User access token
  --user_forks          Save forked repos by user
  -v, --verbose         Logging level=debug
  -f, --force           Force save
  --forks               Save list of forks
  --stars               Save list of stargazers
  --save                Save repos to `save_path`
  --clone               Clone repos to `save_path`
  --bare                Clone a bare git repo
  --recursive           Recursive submodules
  --starred             Get repositories starred by user
  -p SAVE_PATH, --save_path SAVE_PATH
                        Save path to your repos
  -l REPO_LIST [REPO_LIST ...], --repo_list REPO_LIST [REPO_LIST ...]
                        List of repos to clone or to save
```

#### Save list of stargazers to `{user_login}_stargazers.json`: 
`python backup.py -u USER -t TOKEN --stars`

#### Save list of forks to `{user_login}_forks.json`
`python backup.py -u USER -t TOKEN --forks `

#### Download repos to `save_path`
`python backup.py -u USER -t TOKEN --repos -p ~/backups`

#### Clone repos to `save_path`
`python backup.py -u USER -t TOKEN --clone -p ~/backups`
