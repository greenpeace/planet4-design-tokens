#!/usr/bin/env python3

import json
import os
import requests
import semver

GITHUB_API = 'https://api.github.com'
BASE_REPO = 'greenpeace/planet4-design-tokens'
MAIN_BRANCH = 'main'
OAUTH_KEY = os.getenv('GITHUB_OAUTH_TOKEN')
HEADERS = {
    'Authorization': 'token {0}'.format(OAUTH_KEY),
    'Accept': 'application/vnd.github.v3+json'
}

def bump_version(text, prefix='v'):
    """
    Takes a tag number as an argument and increments the minor version.
    """

    # Remove version prefix
    if text.startswith(prefix):
        text = text[len(prefix):]

    # Convert to semver
    if len(text.split('.')) < 3:
        text = '{0}.0'.format(text)

    # Bump minor
    ver = semver.VersionInfo.parse(text)
    next_ver = 'v{0}'.format(str(ver.bump_minor()))

    return next_ver

if __name__ == '__main__':
    tags_endpoint = '{0}/repos/{1}/releases/latest'.format(
        GITHUB_API,
        BASE_REPO
    )

    response = requests.get(tags_endpoint, headers=HEADERS)

    if response.status_code != 404:
        tag_name = bump_version(response.json()['tag_name'])
    else:
        tag_name = bump_version('0.0.0')

    data = {
        'tag_name': tag_name,
        'name': tag_name,
        'body': 'New version of Design Tokens',
    }

    releases_endpoint = '{0}/repos/{1}/releases'.format(
        GITHUB_API,
        BASE_REPO
    )

    response = requests.post(releases_endpoint, headers=HEADERS, data=json.dumps(data))
