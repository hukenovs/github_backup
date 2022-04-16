## GitHub backup repositories
Save your repos and list of stargazers & list of forks for them.

| **Title**     | GitHub Backup       |
|:---|:--------------------|
| **Author**    | Alexander Kapitanov |
| **Sources**   | Python              |
| **Contact**   | `<hidden>`          |
| **Release**   | 16 Apr 2022         |
| **License**   | MIT                 |

### Command line arguments
```bash
usage: backup.py [-h] -u USER_LOGIN [-t USER_TOKEN] [--user_forks] [-v] [--forks] [--stars] [--repos] [--clone] [-p SAVE_PATH]

GitHub saver for stargazers, forks, repos.

optional arguments:
  -h, --help            show this help message and exit
  -u USER_LOGIN, --user_login USER_LOGIN
                        User login
  -t USER_TOKEN, --user_token USER_TOKEN
                        User access token
  --user_forks          Save forked repos by user
  -v, --verbose         Logging level=debug
  --forks               Save list of forks
  --stars               Save list of stargazers
  --repos               Save repos to `save_path`
  --clone               Clone repos to `save_path`
  -p SAVE_PATH, --save_path SAVE_PATH
                        Save path to your repos

```

#### Save list of stargazers to `{user_login}_stargazers.json`: 
`python backup.py -u USER -t TOKEN --stars`

#### Save list of forks to `{user_login}_forks.json`
`python backup.py -u USER -t TOKEN --forks `

#### Download repos to `save_path`
`python backup.py -u USER -t TOKEN --repos -p ~/backups`

#### Clone repos to `save_path`
`python backup.py -u USER -t TOKEN --clone -p ~/backups`
