from collections import OrderedDict
import re
import sys
import json
import openstep_plist


def transform_list_like(d):
    delim = ({'nl': '\n', 'sp': ' '})[d['$delim']]
    return delim.join(d['$elts'])


def from_dict(d, name_key='name'):
    arr = []
    keys = d['$keys'].split('!')
    del d['$keys']
    for k in keys:
        # ignore nonexistent key for convenience
        if k not in d: continue
        d[k][name_key] = k
        arr.append(d[k])
    return arr


def transform(data):
    data['classes'] = from_dict(data['classes'])
    for d in data['classes']:
        if 'code' in d:
            d['code'] = transform_list_like(d['code'])
    data['features'] = from_dict(data['features'])
    for d in data['features']:
        if 'code' in d:
            d['code'] = transform_list_like(d['code'])
    data['glyphs'] = from_dict(data['glyphs'], name_key='glyphname')
    for i in range(len(data['instances'])):
        insts = data['instances']
        keys = insts[i]['$keys'].split('!')
        d = OrderedDict()
        for k in keys:
            d[k] = insts[i][k]
        insts[i] = d


def output(out):
    first = True
    for line in out.split('\n'):
        if not first:
            print()
        first = False
        m = re.match(r'^unicode = (\d+);$', line)
        if m:
            x = m.group(1)
            print(f'unicode = {x:>04};', end='')
        else:
            print(line.replace('\\n', '\\012'), end='')


def main(data):
    transform(data)
    out = openstep_plist.dumps(data, indent='')
    output(out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <FILE>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as fp:
        data = json.load(fp)
    main(data)
