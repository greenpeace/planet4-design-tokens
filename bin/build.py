#!/usr/bin/env python3

import json
import os
import re

JSON_TOKENS_FILE = 'tokens.json'
TOKENS_FILE = '_tokens.scss'

def parse_token_value(value, css_variable):
    if('{' in value):
        if(True == css_variable):
            return 'var(--{0})'.format(re.sub('[{}]+', '', value))
        else:
            return '${0}'.format(re.sub('[{}]+', '', value))

    return value.lower()

def write_lines(token_set_order, tokens_stylesheet, css_variable = True):
    tokens_component_specific = []
    tab = ''

    if True == css_variable:
        tokens_stylesheet.write(':root {\n')
        tab = '  '

    for tokens in token_set_order:
        print('Parse tokens from {0}'.format(JSON_TOKENS_FILE))

        tokens_stylesheet.write('{0}/* Primitives */\n'.format(tab))
        for token_name in sorted(json_data[tokens]):
            token_data = json_data[tokens][token_name]

            value = parse_token_value(token_data['value'], css_variable)

            if True == css_variable:
                line = '{0}--{1}: {2};\n'.format(tab, token_name, value)
            else:
                line = '${0}: {1};\n'.format(token_name, value)

            if "var" not in value and "$" not in value:
                tokens_stylesheet.write(line)
            else:
                tokens_component_specific.append(line)

        tokens_stylesheet.write('{0}/* Component Specific */\n'.format(tab))
        for token_name in tokens_component_specific:
            tokens_stylesheet.write(token_name)

    if True == css_variable:
        tokens_stylesheet.write('}\n')

if __name__ == '__main__':
    tokens_json_path = '{0}/src/{1}'.format(os.getcwd(), JSON_TOKENS_FILE)

    if(os.path.exists(tokens_json_path)):
        print('Open tokens.json file')

        with open(tokens_json_path) as json_file:
            json_data = json.load(json_file)

            if 'tokenSetOrder' in json_data['$metadata']:
                print('Open and update {0} file'.format(TOKENS_FILE))
                tokens_stylesheet = open('{0}/src/{1}'.format(os.getcwd(), TOKENS_FILE), 'w')

                tokens_stylesheet.write('/* CSS Variables */\n')
                write_lines(json_data['$metadata']['tokenSetOrder'], tokens_stylesheet)
                tokens_stylesheet.write('\n/* SASS Variables */\n')
                write_lines(json_data['$metadata']['tokenSetOrder'], tokens_stylesheet, False)

                tokens_stylesheet.close()
                print('Save a new version of {0} file'.format(TOKENS_FILE))
    else:
        print('The {0} file does not exist'.format(JSON_TOKENS_FILE))
        exit(1)

