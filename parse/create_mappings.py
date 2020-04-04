"""
This creates mappings between preeti text and translated text
which will be later used to parse other text(meanings)
"""

def create_mappings(preeti_list, unicode_list):
    zipped = [(x.strip(), y.strip()) for x, y in zip(preeti_list, unicode_list)]
    equal_lengths = [(x, y) for x, y in zipped if len(x) == len(y)]
    one_to_one_mappings = {}

    for x, y in equal_lengths:
        for p, u in zip(x, y):
            existing_map = one_to_one_mappings.get(p, {})
            existing_map[u] = existing_map.get(u, 0) + 1
            one_to_one_mappings[p] = existing_map
    final_one_to_one = {
        k: sorted(v.items(), key=lambda x: x[1], reverse=True)[0][0]
        for k, v in one_to_one_mappings.items()
    }
    print(final_one_to_one)


def main():
    with open('data/just_words.txt') as pf, open('data/just_words_translated.txt') as uf:
        preeti_words = [x for x in pf.read().split() if x]
        unicode_words = [x for x in uf.read().split() if x]

        create_mappings(preeti_words, unicode_words)


if __name__ == '__main__':
    main()
