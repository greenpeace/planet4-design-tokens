#!/usr/bin/env python3

import json
import os
import re

JSON_TOKENS_FILE = 'tokens.json'
SASS_TOKENS_FILE = '_tokens.scss'

def parse_token_value(value):
    if("{" in value):
        return "$%s"%(re.sub('[{}]+', '', value))
    return value

if __name__ == '__main__':
    tokens_json_path = "%s/src/%s"%(os.getcwd(), JSON_TOKENS_FILE)

    if(os.path.exists(tokens_json_path)):
        print('Open tokens.json file')
        ## Open json File
        with open(tokens_json_path) as json_file:
            json_data = json.load(json_file)

            if 'tokenSetOrder' in json_data['$metadata']:
                print('Open and update %s file'%(SASS_TOKENS_FILE))
                tokens_scss = open("%s/src/%s"%(os.getcwd(), SASS_TOKENS_FILE), "w")

                for tokens in json_data['$metadata']['tokenSetOrder']:
                    print('Parse tokens from %s'%(JSON_TOKENS_FILE))
                    for token in json_data[tokens]:
                        token_data = json_data[tokens][token]

                        if 'value' in token_data:
                            tokens_scss.write("$%s: %s;\n"%(token, parse_token_value(token_data['value'])))

                tokens_scss.close()
                print('Save a new version of %s file'%(SASS_TOKENS_FILE))

    else:
        print('The %s file does not exist'%(JSON_TOKENS_FILE))

