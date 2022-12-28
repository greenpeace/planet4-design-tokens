#!/usr/bin/env python3

import json
import os
import requests
import sys
import shutil
from git import Repo, Actor

# TODO:
# - Assign reviewers

GITHUB_API = 'https://api.github.com'
BASE_TOKENS_REPO = 'greenpeace/planet4-design-tokens'
BASE_REPO = 'greenpeace/planet4-master-theme'
MAIN_BRANCH = 'main'
OAUTH_KEY = os.getenv('GITHUB_OAUTH_TOKEN')
GITHUB_REPO_PREFIX = 'https://{0}@github.com/'.format(OAUTH_KEY)
HEADERS = {
    'Authorization': 'token {0}'.format(OAUTH_KEY),
    'Accept': 'application/vnd.github.v3+json'
}
AUTHOR_NAME = 'CircleCI Bot'
AUTHOR_EMAIL = os.getenv('GIT_USER_EMAIL')
TOKENS_SCSS_FILE = '_tokens.scss'

def create_pull_request(title, branch, diff):
    body = '**New version of Design Tokens**<br> {0}'.format(diff)

    repo_endpoint = '{0}/repos/{1}/pulls'.format(
        GITHUB_API,
        BASE_REPO
    )
    data = {
        'head': branch,
        'base': MAIN_BRANCH,
        'title': title,
        'body': body
    }
    response = requests.post(repo_endpoint, headers=HEADERS, data=json.dumps(data))

    return response.json()['url']

if __name__ == '__main__':
    directory_name = sys.argv[1]

    try:
        print('checking {0}/{1}'.format(directory_name, TOKENS_SCSS_FILE))
        tokens_file = open('{0}/{1}'.format(directory_name, TOKENS_SCSS_FILE), 'r').close()
    except:
        print('Tokens file does not exist')
        exit(1)

    tokens_releases_endpoint = '{0}/repos/{1}/releases'.format(
        GITHUB_API,
        BASE_TOKENS_REPO
    )

    response = requests.get(tokens_releases_endpoint, headers=HEADERS)
    json_response = response.json()

    diff = {}

    try:
        newest_tag = json_response[0]['tag_name']

        if(len(json_response) == 1):
            diff = 'https://github.com/{0}/compare/{1}...{2}'.format(BASE_TOKENS_REPO, newest_tag, newest_tag)
        else:
            latest_tag = json_response[1]['tag_name']
            diff = 'https://github.com/{0}/compare/{1}...{2}'.format(BASE_TOKENS_REPO, latest_tag, newest_tag)
    except IndexError:
        print('Design Tokens has no releases yet.')
        exit(1)

    print('Cloning base repo...')
    theme_repo = Repo.clone_from('{0}{1}.git'.format(GITHUB_REPO_PREFIX, BASE_REPO), 'theme')

    branch = 'design-tokens-{0}'.format(newest_tag)

    print('Switch to branch {0}...'.format(branch))
    head = theme_repo.create_head(branch)
    theme_repo.head.reference = head

    dest_file = '{0}/assets/src/scss/base/{1}'.format(theme_repo.working_tree_dir, TOKENS_SCSS_FILE)

    shutil.move(
        '{0}/{1}'.format(directory_name, TOKENS_SCSS_FILE),
        dest_file
    )

    file_list = [
        dest_file
    ]

    staged = theme_repo.index.add(file_list)
    print('Changes staged: {0}'.format(staged))

    author = Actor(AUTHOR_NAME, AUTHOR_EMAIL)

    commit_message = 'Design Tokens: New release [{0}]\n\n- Changes commited by {1}'.format(newest_tag, AUTHOR_NAME)
    commit = theme_repo.index.commit(commit_message, author=author, committer=author)

    origin = theme_repo.remotes['origin']
    ref = origin.push(branch)
    print('Changes pushed to {0}'.format(ref[0].remote_ref.name))
    pull = create_pull_request('Design Tokens: New release [{0}]'.format(newest_tag), branch, diff)
    print('Pull Request created at {0}'.format(pull))
    print('Design Tokens promoted.')
