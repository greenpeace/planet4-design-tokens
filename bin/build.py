#!/usr/bin/env python3

import json
import os
import re

JSON_TOKENS_FILE = 'tokens.json'
TOKENS_FILE = '_tokens.css'

def parse_token_value(value):
    if('{' in value):
        return 'var(--{0})'.format(re.sub('[{}]+', '', value))
    return value.lower()

if __name__ == '__main__':
    tokens_json_path = '{0}/src/{1}'.format(os.getcwd(), JSON_TOKENS_FILE)

    if(os.path.exists(tokens_json_path)):
        print('Open tokens.json file')

        with open(tokens_json_path) as json_file:
            json_data = json.load(json_file)

            if 'tokenSetOrder' in json_data['$metadata']:
                print('Open and update {0} file'.format(TOKENS_FILE))
                tokens_scss = open('{0}/src/{1}'.format(os.getcwd(), TOKENS_FILE), 'w')

                tokens_component_specific = []

                tokens_scss.write(':root {\n')

                for tokens in json_data['$metadata']['tokenSetOrder']:
                    print('Parse tokens from {0}'.format(JSON_TOKENS_FILE))

                    tokens_scss.write('\t/* Primitives */\n')
                    for token in sorted(json_data[tokens]):
                        token_data = json_data[tokens][token]

                        value = parse_token_value(token_data['value'])
                        line = '\t--{0}: {1};\n'.format(token, parse_token_value(token_data['value']))
                        if "var" not in value:
                            tokens_scss.write(line)
                        else:
                            tokens_component_specific.append(line)

                    tokens_scss.write('\t/* Component Specific */\n')
                    for token in tokens_component_specific:
                        tokens_scss.write(token)

                tokens_scss.write('}')
                tokens_scss.close()
                print('Save a new version of {0} file'.format(TOKENS_FILE))
    else:
        print('The {0} file does not exist'.format(JSON_TOKENS_FILE))
        exit(1)

