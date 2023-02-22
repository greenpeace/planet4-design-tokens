#!/usr/bin/env python3

import json
import os
import requests
import sys
import shutil
from git import Repo, Actor

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
TOKENS_STYLESHEET = '_tokens.scss'

def add_labels(pull):
    pull_number = pull['number']

    try:
        endpoint_labels = '{0}/repos/greenpeace/planet4-master-theme/issues/{1}/labels'.format(GITHUB_API, pull_number)
        requests.post(endpoint_labels, headers=HEADERS,data=json.dumps({
            'labels': ['Design Tokens']
        }))
    except IndexError:
        print('Error when add a comment to #{0}'.format(pull_number))

def request_reviwers(pull):
    pull_number = pull['number']

    try:
        team_reviewers = [ 'planet-4-developers' ]

        data = {
            'team_reviewers': team_reviewers
        }

        endpoint_pull = '{0}/repos/greenpeace/planet4-master-theme/pulls/{1}/requested_reviewers'.format(GITHUB_API, pull_number)
        requests.post(endpoint_pull, headers=HEADERS,data=json.dumps(data))
    except IndexError:
        print('Error when assigne reviewers to #{0}'.format(pull_number))

    print('@{0} members were been assigned to #{1}'.format(len(team_reviewers), pull['url']))

def add_pull_comment(pull):
    pull_number = pull['number']

    try:
        planet_4_designers = 'greenpeace/planet-4-designers'

        message = 'Hey @{0}, a new Design Tokens version has been promoted to the master theme.\nPlease check after the test instance it is ready :rocket:.'.format(planet_4_designers)

        data = {
            'body': message
        }

        endpoint_pull = '{0}/repos/greenpeace/planet4-master-theme/issues/{1}/comments'.format(GITHUB_API, pull_number)
        requests.post(endpoint_pull, headers=HEADERS,data=json.dumps(data))
    except IndexError:
        print('Error when add a comment to #{0}'.format(pull_number))

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

    if(response.status_code == 200 or response.status_code == 201):
        pull = response.json()
        print('Pull Request created at {0}'.format(pull['url']))
        add_labels(pull)
        request_reviwers(pull)
        add_pull_comment(pull)

if __name__ == '__main__':
    directory_name = sys.argv[1]

    try:
        print('checking {0}/{1}'.format(directory_name, TOKENS_STYLESHEET))
        tokens_file = open('{0}/{1}'.format(directory_name, TOKENS_STYLESHEET), 'r').close()
    except:
        print('Tokens file does not exist')
        exit(1)

    tokens_releases_endpoint = '{0}/repos/{1}/releases'.format(
        GITHUB_API,
        BASE_TOKENS_REPO
    )

    response = requests.get(tokens_releases_endpoint, headers=HEADERS)
    json_response = response.json()

    try:
        newest_tag = json_response[0]['tag_name']

        if(len(json_response) == 1):
            latest_tag = newest_tag
        else:
            latest_tag = json_response[1]['tag_name']
    except IndexError:
        print('Design Tokens has no releases yet.')
        exit(1)

    diff = 'https://github.com/{0}/compare/{1}...{2}'.format(BASE_TOKENS_REPO, latest_tag, newest_tag)

    print('Cloning base repo...')
    theme_repo = Repo.clone_from('{0}{1}.git'.format(GITHUB_REPO_PREFIX, BASE_REPO), 'theme')

    branch = 'design-tokens-{0}'.format(newest_tag)

    print('Switch to branch {0}...'.format(branch))
    head = theme_repo.create_head(branch)
    theme_repo.head.reference = head

    dest_file = '{0}/assets/src/scss/base/{1}'.format(theme_repo.working_tree_dir, TOKENS_STYLESHEET)

    shutil.move(
        '{0}/{1}'.format(directory_name, TOKENS_STYLESHEET),
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

    create_pull_request('Design Tokens: New release [{0}]'.format(newest_tag), branch, diff)
    print('Design Tokens promoted.')
