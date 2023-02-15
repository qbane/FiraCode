import sys
import json
import openstep_plist


def detect_delim(s):
    if '\n' in s:
        return 'nl', '\n'
    elif ' ' in s:
        return 'sp', ' '
    else:
        return '', None


def transform_list_like(s):
    x, delim = detect_delim(s)
    assert delim is not None
    return {
        '$delim': x,
        '$elts': s.split(delim),
    }


def to_dict(arr, name_key='name'):
    ret = {}
    keys = []
    for val in arr:
        assert name_key in val
        key = val[name_key]
        keys.append(key)
        assert key not in ret
        ret[key] = val
        del val[name_key]
    ret['$keys'] = '!'.join(keys)
    return ret


def transform(data):
    for d in data['classes']:
        if 'code' in d:
            d['code'] = transform_list_like(d['code'])
    data['classes'] = to_dict(data['classes'])

    for d in data['features']:
        if 'code' in d:
            d['code'] = transform_list_like(d['code'])
    data['features'] = to_dict(data['features'])

    data['glyphs'] = to_dict(data['glyphs'], name_key='glyphname')
    for inst in data['instances']:
        inst['$keys'] = '!'.join(inst.keys())


def main(data):
    if 0:
        # unexport liga from source
        expglys = set()
        for d in data['glyphs']:
            if d['glyphname'].endswith('.liga'):
                d['export'] = 0
            if d.get('export') != 0:
                expglys.add(d['glyphname'])
        # if a glyph is not exported, remove it from class
        for kl in data['classes']:
            _, d = detect_delim(kl['code'])
            assert d is not None
            gs = list(filter(lambda x: x in expglys, kl['code'].split(d)))
            kl['code'] = d.join(gs)

    # delete some data for easier diffing
    if 1:
        for d in data['glyphs']:
            # if d.get('export') == 0:
            #     # print(d['glyphname'])
            #     del d['export']
            if 'lastChange' in d: d['lastChange'] = None
            if 'layers' in d: d['layers'] = None

    transform(data)
    # out = openstep_plist.dumps(data, fp, indent='')
    # print(out.replace('\\n', '\\012'))
    text = json.dumps(data, sort_keys=True, indent=2)
    print(text)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <FILE>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as fp:
        data = openstep_plist.load(fp, use_numbers=True)
    main(data)
