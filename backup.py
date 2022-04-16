r"""GitHub Backup Repos

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
  --clone               Can clone repos to `save_path`
  -p SAVE_PATH, --save_path SAVE_PATH
                        Save path to your repos

"""

import os
import json
import argparse
import logging
import requests
from typing import Optional
from functools import cached_property


logger = logging.getLogger(__name__)


class GithubSaver:
    API_URL = "https://api.github.com/"
    HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "",
    }

    def __init__(self, user_login: str, user_token: Optional[str] = None, user_forks: bool = False):
        self._user_login = user_login
        self._user_forks = user_forks
        self.__user_token = user_token
        if user_token is not None:
            self.HEADERS.update({"Authorization": user_token})

    def __repositories(self, clone_url: bool = False) -> list:
        response = self.__response(self.API_URL, stage=f"users/{self._user_login}/repos")
        if response.status_code == 200:
            repos = []
            for repo in response.json():
                if not self._user_forks and repo['fork']:
                    continue

                url_path = repo['clone_url'] if clone_url else repo['url']
                repos.append(url_path)
            return repos
        else:
            raise Exception(f"Cannot get list of repos from {self._user_login}")

    @property
    def user_login(self):
        return self._user_login

    @user_login.setter
    def user_login(self, value: str):
        self._user_login = value

    @cached_property
    def repositories(self) -> list:
        return self.__repositories()

    @cached_property
    def clone_links(self) -> list:
        return self.__repositories(clone_url=True)

    def __response(self, url: str, stage: str = "") -> requests.Response:
        return requests.get(
            url=os.path.join(url, stage),
            headers=self.HEADERS
        )

    def __save_list(self, destination: str):
        """Save list"""
        if destination == "stargazers":
            method = self.get_stargazers
        elif destination == "forks":
            method = self.get_forks
        else:
            raise NotImplemented(f"IMplement method for {destination}")

        repo_dict = {}
        for repo_url in self.repositories:
            repo_name = os.path.basename(repo_url)
            if result := method(repo_url):
                repo_dict[repo_name] = result

        save_path = f"{self._user_login}_{destination}.json"
        with open(save_path, "w") as f:
            json.dump(repo_dict, f)

    def save_stargazers(self):
        """Save all stargazers"""
        self.__save_list(destination="stargazers")

    def save_forks(self):
        """Save all forks"""
        self.__save_list(destination="forks")

    def save_repos(self, save_path: str = "."):
        """Save all repos"""

        for repo_url in self.repositories:
            repo_name = os.path.basename(repo_url)
            repo_resp = requests.get(url=os.path.join(repo_url, "zipball"))
            if repo_resp.status_code == 200:
                with open(os.path.join(save_path, f"{repo_name}.zip"), 'wb') as ff:
                    ff.write(repo_resp.content)
            else:
                logger.warning(f"Cannot download repo {repo_resp}")

    def clone_repos(self, clone_path: str = "."):
        """Save all repos"""
        for repo_url in self.clone_links:
            logger.info(f"Clone {repo_url}")
            repo_name, _ = os.path.splitext(os.path.basename(repo_url))
            repo_path = os.path.join(clone_path, repo_name)

            if self.__user_token:
                repo_url = repo_url.replace("github.com", f"{self._user_login}:{self.__user_token}@github.com")

            try:
                os.system(f"git clone {repo_url} {repo_path}")
            except SystemError:
                logger.warning(f"Cannot clone {repo_url}")

    def get_stargazers(self, url: str) -> list:
        """Get all stargazers"""

        response = self.__response(url, "stargazers")
        if response.status_code == 200:
            star_list = []
            for gazer in response.json():
                star_list.append(
                    {
                        'login': gazer['login'],
                        'id': gazer['id'],
                        'node_id': gazer['node_id'],
                    }
                )
            logger.info(f"Get stargazers for {url}")
            return star_list
        else:
            logger.warning(f"Cannot get stargazers for {url}")

    def get_forks(self, url: str) -> list:
        """Get all forks"""

        response = self.__response(url, "forks")
        if response.status_code == 200:
            fork_list = []
            for fork in response.json():
                fork_list.append(
                    {
                        'login': fork['owner']['login'],
                        'id': fork['id'],
                        'node_id': fork['node_id'],
                    }
                )
            logger.info(f"Get forks for {url}")
            return fork_list
        else:
            logger.warning(f"Cannot get forks for {url}")


def __parser_github():
    parser = argparse.ArgumentParser(description="GitHub saver for stargazers, forks, repos.")

    parser.add_argument("-u", "--user_login", type=str, required=True, help=f"User login")
    parser.add_argument("-t", "--user_token", type=str, default=None, help=f"User access token")
    parser.add_argument("--user_forks", action="store_true", help=f"Save forked repos by user")
    parser.add_argument("-v", "--verbose", action="store_true", help=f"Logging level=debug")

    parser.add_argument("--forks", action="store_true", help=f"Save list of forks")
    parser.add_argument("--stars", action="store_true", help=f"Save list of stargazers")
    groups = parser.add_mutually_exclusive_group()
    parser.add_argument("--repos", action="store_true", help=f"Save repos to `save_path`")
    groups.add_argument("--clone", action="store_true", help=f"Clone repos to `save_path`")
    parser.add_argument("-p", "--save_path", type=str, default=".", help=f"Save path to your repos")

    args, _ = parser.parse_known_args()

    for kk, vv in vars(args).items():
        print(f"{kk :<20}: {vv}")

    logging.basicConfig(
        format=u'[LINE:%(lineno)d] %(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    github_saver = GithubSaver(
        user_login=args.user_login,
        user_token=args.user_token,
        user_forks=args.user_forks,
    )

    if args.stars:
        github_saver.save_stargazers()
    if args.forks:
        github_saver.save_forks()
    if args.repos:
        github_saver.save_repos(save_path=args.save_path)
    if args.clone:
        github_saver.clone_repos(clone_path=args.save_path)


if __name__ == '__main__':
    __parser_github()
