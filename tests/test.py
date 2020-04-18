import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from convert import preeti_to_unicode


def test_conversion_pairs():
    fail = False
    with open('./conversion_pairs.txt') as testfile:
        for i, line in enumerate(testfile):
            stripped = line.strip()
            if not stripped:
                continue
            preeti, uni = stripped.split(' ==> ')
            converted = preeti_to_unicode(preeti)
            if uni != converted:
                fail = True
                print(f'Expected "{uni}" for "{preeti}", Obtained "{converted}"')
    if not fail:
        print('Tests passed')
    else:
        print('FAIL...')


if __name__ == '__main__':
    test_conversion_pairs()
