import json

from convert import preeti_to_unicode


def main():
    with open('data/words_meanings.json') as rawfile, \
            open('data/words_meanings_converted.json', 'w', encoding='utf-8') as conv_file:
        raw_data = json.load(rawfile)
        converted_data = {}
        for k, v in raw_data.items():
            meanings = [preeti_to_unicode(x) for x in v['meanings']]
            meta = [preeti_to_unicode(x) for x in v.get('meta', [])]
            converted_data[preeti_to_unicode(k)] = {
                'meanings': meanings,
                'meta': meta,
            }
        # print(json.dumps(converted_data, indent=2, ensure_ascii=False))
        json.dump(converted_data, conv_file, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
