'''Given a YAML or JSON document where some mappings contain multiple 
instances of the same key, create a document that only differs in that those 
mappings have been converted into lists.
For instance,
blu:
    1: 2
    1: 3
    2: 4
would be rendered as {'blu': {1: [2, 3], 2: 4}} by convert_multi_keys,
rather than {'blu': 1: 3, 2: 4}, which is what yaml.safe_load would return.

This is not intended to process YAML documents that have any fancy features
like serialized Python objects or the like. The only scalar types allowed are
int, float, bool, str, and None.

Note that this works on JSON as well as YAML even though it uses the YAML 
parser because JSON is a subset of YAML.

Performance-wise, convert_multi_keys seems to be slightly slower than
yaml.safe_load, but it is MUCH slower than json.loads.

Unlike yaml.safe_load, which will crash on any file that has lines with
leading tabs, this replaces all leading tabs with leading spaces (default 4),
because some JSON files have leading tabs.
See convert_leading_tabs for this convenience function.
'''
import yaml
from ast import literal_eval
from collections import Counter
import re

TAG_TYPE_MAP = {'int': int, 'float': float, 'bool': bool, 'null': lambda x: None}

def convert_multi_keys(yamtxt):
    def parse_scalar(scalar_node):
        tag_type = re.findall('\d{4,}:(\w+)$', scalar_node.tag)[0]
        converter = TAG_TYPE_MAP.get(tag_type)
        if converter:
            return converter(scalar_node.value)
        else:
            return str(scalar_node.value)
    
    def handle_node(arr, node, key = None):
        if key is None:
            if isinstance(node, yaml.ScalarNode):
                arr.append(parse_scalar(node))
            elif isinstance(node, yaml.MappingNode):
                arr.append(search(node, {}))
            else:
                arr.append(search(node, []))
        else:
            if isinstance(node, yaml.ScalarNode):
                arr[key] = parse_scalar(node)
            elif isinstance(node, yaml.MappingNode):
                arr[key] = search(node, {})
            else:
                arr[key] = search(node, [])
    
    def search(yamc, out):
        if isinstance(yamc, yaml.MappingNode):
            key_count = Counter(parse_scalar(key) for key,val in yamc.value)
            # print(f'{key_count = }')
            for key,val in yamc.value:
                key = parse_scalar(key)
                # print(f'{key_count[key] =  }, {key = }')
                if key_count[key] > 1:
                    out.setdefault(key, [])
                    handle_node(out[key], val)
                else:
                    handle_node(out, val, key)
        else:
            for item in yamc.value:
                handle_node(out, item)
        
        return out
    
    yamc = yaml.compose(convert_leading_tabs(yamtxt))
    if isinstance(yamc, yaml.MappingNode):
        out = {}
    else:
        out = []
    
    return search(yamc, out)


def _convert_re_match(m, tabs_per_space):
    return tabs_per_space * ' ' * len(m.group())


def convert_leading_tabs(string, spaces_per_tab = 4):
    '''takes all '\t' at the start of any lines in string and replaces them with spaces_per_tab ' ' characters per '\t' excised.
    Does not touch any '\t' characters not at the start of a line.'''
    converter = lambda x: _convert_re_match(x, spaces_per_tab)
    
    return '\n'.join(re.sub('^\t+', converter, line) 
                    for line in string.split('\n')) 


def CLI(yaml_fname):
    '''Read a YAML file and print out a YAML document modified by applying
    convert_multi_keys to the original.'''
    with open(yaml_fname) as f:
        txt = f.read()
    
    return yaml.safe_dump(convert_multi_keys(txt))


def test():
    yamtxt = '''fuqj:
    blu: [1., 1.5]
    blu: True
    foo: [3, 4]
    1: 5.
    1: null
me: zu'''
    yamtxt_normal_out = {'fuqj': {'blu': True, 'foo': [3, 4], 1: None}, 'me': 'zu'}
    # note that yamtxt_normal_out only includes the last instance of each
    # key-value pair whenever there were duplicate keys, because hashmaps
    # can only have one pair for each unique key.
    yamtxt_multikey_out = {'fuqj': {'blu': [[1., 1.5], True], 
                                    'foo': [3, 4], 
                                    1: [5., None]},
                           'me': 'zu'}
    if yamtxt_multikey_out != convert_multi_keys(yamtxt):
        print(f'THIS MODULE DOES NOT WORK!\n{yamtxt}\nshould have been parsed as {yamtxt_multikey_out} but was instead parsed as {convert_multi_keys(yamtxt)}')
    # now test on some JSON documents that have no duplicate keys    
    for yamtxt in ['{}', '[]', "['a', 'b', {'a': 1, 'b': 2}]", '[1,2]']:
        true_out, my_out = literal_eval(yamtxt), convert_multi_keys(yamtxt)
        assert true_out == my_out, \
            f'{yamtxt} should have been parsed by convert_multi_keys as {true_out}, got {my_out}'
    
    convtabs_in = '\ta\tb\n\tb'
    convtabs = convert_leading_tabs(convtabs_in, 2)
    convtabs_true = '  a\tb\n  b'
    assert convtabs == convtabs_true, \
       f'convert_leading_tabs({convtabs_in:r}) should have given {convtabs_true:r}, gave {convtabs:r}'


if __name__ == '__main__':
    import sys
    try:
        fname = ' '.join(sys.argv[1:])
        if fname != '':
            print(CLI(fname))
    except FileNotFoundError as ex:
        print(ex)
