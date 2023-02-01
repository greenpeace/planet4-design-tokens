#!/usr/bin/env python3

import json
import os
import re

JSON_TOKENS_FILE = 'tokens.json'
SASS_TOKENS_FILE = '_tokens.scss'

def parse_token_value(value):
    if('{' in value):
        return '${0}'.format(re.sub('[{}]+', '', value))
    return value.lower()

if __name__ == '__main__':
    tokens_json_path = '{0}/src/{1}'.format(os.getcwd(), JSON_TOKENS_FILE)

    if(os.path.exists(tokens_json_path)):
        print('Open tokens.json file')

        with open(tokens_json_path) as json_file:
            json_data = json.load(json_file)

            if 'tokenSetOrder' in json_data['$metadata']:
                print('Open and update {0} file'.format(SASS_TOKENS_FILE))
                tokens_scss = open('{0}/src/{1}'.format(os.getcwd(), SASS_TOKENS_FILE), 'w')

                for tokens in json_data['$metadata']['tokenSetOrder']:
                    print('Parse tokens from {0}'.format(JSON_TOKENS_FILE))
                    for token in json_data[tokens]:
                        token_data = json_data[tokens][token]

                        if 'value' in token_data:
                            tokens_scss.write('${0}: {1};\n'.format(token, parse_token_value(token_data['value'])))

                tokens_scss.close()
                print('Save a new version of {0} file'.format(SASS_TOKENS_FILE))

    else:
        print('The {0} file does not exist'.format(JSON_TOKENS_FILE))
        exit(1)

