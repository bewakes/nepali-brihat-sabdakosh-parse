import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from convert import preeti_to_unicode


def test_conversion_pairs():
    with open('./conversion_pairs.txt') as testfile:
        for i, line in enumerate(testfile):
            stripped = line.strip()
            if not stripped:
                continue
            preeti, uni = stripped.split(' ==> ')
            converted = preeti_to_unicode(preeti)
            assert uni == converted, f'Expected "{uni}" for "{preeti}", Obtained "{converted}"'
    print('Tests passed')


if __name__ == '__main__':
    test_conversion_pairs()
