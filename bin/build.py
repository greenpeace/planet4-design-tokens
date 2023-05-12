#!/usr/bin/env python3

import json
import os
import re

JSON_TOKENS_FILE = 'tokens.json'
TOKENS_FILE = '_tokens.scss'

def parse_token_name(value):
    # Remove empty spaces, replace to `-` and convert to lower case.
    return re.sub('[ ]+', '-', value).lower()

def parse_token_value(value, css_variable):
    if type(value) is dict:
        return None
    else:
        if('{' in value):
            if(True == css_variable):
                return 'var(--{0})'.format(re.sub('[{}]+', '', value))
            else:
                return '${0}'.format(re.sub('[{}]+', '', value))

    # This means an hexa color value
    if('#' in value):
        return value.lower()
    else:
        return '"{0}"'.format(value)

def parse_line(token_name, value, tab, css_variable):
    token_name = parse_token_name(token_name)
    if True == css_variable:
        return '{0}--{1}: {2};\n'.format(tab, token_name, value)
    else:
        return '{0}${1}: {2};\n'.format(tab, token_name, value)

def write_line(value, line, tokens_primitives, tokens_component_specific):
    # Having `var()` or `$` means that are component spcific token
    if "var" not in value and "$" not in value:
        tokens_primitives.write(line)
    else:
        tokens_component_specific.append(line)

def read_json_data(token_set_order, tokens_stylesheet, css_variable = True):
    tokens_component_specific = []
    tab = ''

    if True == css_variable:
        tokens_stylesheet.write(':root {\n')
        tab = '  '

    for tokens in token_set_order:
        print('Parse tokens from {0}\n'.format(JSON_TOKENS_FILE))

        # Primitive Tokens
        tokens_stylesheet.write('{0}/* Primitives */\n'.format(tab))
        for token_name in sorted(json_data[tokens]):
            token_data = json_data[tokens][token_name]

            # Group doesn't include the value as field
            if 'value' in token_data:
                value = parse_token_value(token_data['value'], css_variable)

                if value is None:
                    print('The value of {0} cannot be parsed as a regular token'.format(token_name))
                else:
                    line = parse_line(token_name, value, tab, css_variable)
                    write_line(value, line, tokens_stylesheet, tokens_component_specific)
            else:
                print('Parse tokens related to "{0}"'.format(token_name))

                # Find the associated value of the token_name
                for _ in json_data[tokens]:
                    if 'value' in json_data[tokens][_] and token_name == json_data[tokens][_]['value']:
                        token_name = parse_token_name(_)

                for token_property in token_data:
                    value = token_data[token_property]['value']
                    line = parse_line('{0}--{1}'.format(token_property, token_name), value, tab, css_variable)
                    write_line(value, line, tokens_stylesheet, tokens_component_specific)

        # Component Specific Tokens
        tokens_stylesheet.write('{0}/* Component Specific */\n'.format(tab))
        for token in tokens_component_specific:
            tokens_stylesheet.write(token)

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

                tokens_stylesheet.write('/* This is an auto-generated file. */\n\n')
                tokens_stylesheet.write('/* CSS Variables */\n')
                read_json_data(json_data['$metadata']['tokenSetOrder'], tokens_stylesheet)
                tokens_stylesheet.write('\n/* SASS Variables */\n')
                read_json_data(json_data['$metadata']['tokenSetOrder'], tokens_stylesheet, False)

                tokens_stylesheet.close()
                print('Save a new version of {0} file'.format(TOKENS_FILE))
    else:
        print('The {0} file does not exist'.format(JSON_TOKENS_FILE))
        exit(1)

