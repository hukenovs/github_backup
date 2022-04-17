r"""GitHub saver for stargazers, forks, repos. Can clone all user repos.
"""

import os
import json
import argparse
import logging
import requests
from typing import Optional
from functools import cached_property


logger = logging.getLogger(__name__)


class GitHubSaver:
    """GitHub Saver (download or clone user repos or starred repos, save stargazers and list of forks)

    Parameters
    ----------
    user_login: str
        GitHub user login

    user_token: Optional[str]
        GitHub user access token. May be left.

    user_forks: bool
        Save forked repos by user. Default: False.

    """
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

    @property
    def user_login(self):
        return self._user_login

    @user_login.setter
    def user_login(self, value: str):
        self._user_login = value

    def __response(self, url: str, stage: str = "") -> requests.Response:
        return requests.get(
            url=os.path.join(url, stage),
            headers=self.HEADERS
        )

    def __api_request(self, stage: str) -> dict:
        response = self.__response(self.API_URL, stage=f"users/{self._user_login}/{stage}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Cannot get list of repos from {self._user_login}")

    @cached_property
    def _repositories(self) -> dict:
        return self.__api_request(stage='repos')

    @cached_property
    def _starred_list(self) -> dict:
        return self.__api_request(stage='starred')

    def _remote_request(self, content: dict, clone_url: bool = False) -> list:
        repos = []
        for repo in content:
            if not self._user_forks and repo['fork']:
                continue

            url_path = repo['clone_url'] if clone_url else repo['url']
            repos.append(url_path)
        return repos

    @cached_property
    def owner_repositories(self) -> list:
        """List of user repositories"""
        return self._remote_request(content=self._repositories)

    @cached_property
    def owner_clone_links(self) -> list:
        """List of user repositories in clone link format"""
        return self._remote_request(content=self._repositories, clone_url=True)

    @cached_property
    def user_starred_list(self):
        """List of repos starred by user"""
        return self._remote_request(content=self._starred_list)

    @cached_property
    def user_starred_links(self):
        """List of links to repos starred by user"""
        return self._remote_request(content=self._starred_list, clone_url=True)

    def __save_list(self, destination: str):
        """Save list to json"""
        if destination == "stargazers":
            method = self.get_stargazers
        elif destination == "forks":
            method = self.get_forks
        else:
            raise NotImplemented(f"Implement method for {destination}")

        repo_dict = {}
        for repo_url in self.owner_repositories:
            repo_name = os.path.basename(repo_url)
            if result := method(repo_url):
                repo_dict[repo_name] = result

        save_path = f"{self._user_login}_{destination}.json"
        with open(save_path, "w") as f:
            json.dump(repo_dict, f, indent=2, ensure_ascii=True)

    def save_stargazers(self):
        """Save all stargazers"""
        self.__save_list(destination="stargazers")

    def save_forks(self):
        """Save all forks"""
        self.__save_list(destination="forks")

    def save_repos(self, save_path: str = ".", force: bool = False, starred: bool = False):
        """Save all repos"""
        repositories = self.user_starred_list if starred else self.owner_repositories

        for repo_url in repositories:
            repo_name = os.path.basename(repo_url)
            repo_resp = requests.get(url=os.path.join(repo_url, "zipball"))
            if repo_resp.status_code == 200:
                repo_path = os.path.join(save_path, f"{repo_name}.zip")
                logger.info(f"Save {repo_url} to {repo_path}")

                if force or not os.path.isfile(repo_path):
                    with open(repo_path, 'wb') as ff:
                        ff.write(repo_resp.content)
                else:
                    logger.info(f"Repo {repo_resp} is already saved!")

            else:
                logger.warning(f"Cannot download repo {repo_resp}")

    def clone_repos(self, clone_path: str = ".", bare: bool = False, recursive: bool = False, starred: bool = False):
        """Save all repos"""
        repositories = self.user_starred_links if starred else self.owner_clone_links

        for repo_url in repositories:
            repo_name, _ = os.path.splitext(os.path.basename(repo_url))
            repo_path = os.path.join(clone_path, repo_name)
            logger.info(f"Clone {repo_url} to {repo_path}")

            if self.__user_token:
                repo_url = repo_url.replace("github.com", f"{self._user_login}:{self.__user_token}@github.com")

            command = f"git clone {repo_url} {repo_path}" + " --bare" * bare + " --recursive" * recursive
            try:
                os.system(command)
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

    parser.add_argument("-u", "--user_login", type=str, required=True, help="User login")
    parser.add_argument("-t", "--user_token", type=str, default=None, help="User access token")
    parser.add_argument("--user_forks", action="store_true", help="Save forked repos by user")
    parser.add_argument("-v", "--verbose", action="store_true", help="Logging level=debug")
    parser.add_argument("-f", "--force", action="store_true", help="Force save")

    parser.add_argument("--forks", action="store_true", help="Save list of forks")
    parser.add_argument("--stars", action="store_true", help="Save list of stargazers")
    groups = parser.add_mutually_exclusive_group()
    groups.add_argument("--save", action="store_true", help="Save repos to `save_path`")
    groups.add_argument("--clone", action="store_true", help=f"Clone repos to `save_path`")
    parser.add_argument("--bare", action="store_true", help="Clone a bare git repo")
    parser.add_argument("--recursive", action="store_true", help="Recursive submodules")
    parser.add_argument("--starred", action="store_true", help="Get repositories starred by user")
    parser.add_argument("-p", "--save_path", type=str, default=".", help="Save path to your repos")
    parser.add_argument("-l", "--repo_list", nargs="+", help="List of repos to clone or to save")
    # TODO: Implement repo list for saving custom repositories from input arguments.

    args, _ = parser.parse_known_args()

    for kk, vv in vars(args).items():
        if vv:
            print(f"{kk :<20}: {vv}")

    logging.basicConfig(
        format=u'[LINE:%(lineno)d] %(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    github_saver = GitHubSaver(
        user_login=args.user_login,
        user_token=args.user_token,
        user_forks=args.user_forks,
    )

    if args.stars:
        github_saver.save_stargazers()

    if args.forks:
        github_saver.save_forks()

    if args.save:
        github_saver.save_repos(
            save_path=args.save_path,
            force=args.force,
            starred=args.starred,
        )

    if args.clone:
        github_saver.clone_repos(
            clone_path=args.save_path,
            bare=args.bare,
            recursive=args.recursive,
            starred=args.starred,
        )


if __name__ == '__main__':
    __parser_github()
