import re
import os
import ruamel.yaml
from io import StringIO


def escape_json(text):
    if '{{' in text:
        return re.sub(r"\s(?={^\{\}}*}})", "_", text)
    else:
        return text


def convert_to_yaml(data, options=None):
    yaml = ruamel.yaml.YAML()
    yaml.default_flow_style = False
    if options == None: options = {}
    string_stream = StringIO()
    yaml.dump(data, string_stream, **options)
    output_str = string_stream.getvalue()
    string_stream.close()
    return output_str

def load_yaml(file):
    yaml = ruamel.yaml.YAML(typ='safe', pure=True)
    with open(file) as stream:
        return yaml.load(stream)

def save_yaml_to_file(file, content):
    yaml = ruamel.yaml.YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=4)
    with open(file, 'wb') as f:
        yaml.dump(content, f)

def find_keys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in find_keys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find_keys(j, kv):
                yield x
