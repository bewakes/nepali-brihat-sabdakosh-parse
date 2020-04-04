"""
This module contains functions that parse the words and meanings text
"""

from bs4 import BeautifulSoup
import os
import sys
import json


def parse_words(html: str) -> None:
    """
    Parse the html and return dict of words and meaning text
    """
    words_meanings: dict = {}

    soup = BeautifulSoup(html, 'html5lib')

    divs = soup.findAll('div')
    for div in divs[1:]:  # ignore first div, it's just page number
        spans = div.findAll('span')
        if len(spans) < 2:
            continue

        if 'AICLBD+Himalayabold' in spans[0]['style']:
            word = spans[0].text
            data = {}
            square_brace_count = 0

            temp_meta = []
            for span in spans[1:]:
                if 'AICLFF+TimesNewRoman' in span['style'] and span.text in ['[', ']']:
                    if span.text == '[':
                        square_brace_count += 1
                    else:
                        square_brace_count -= 1
                        data['meta'] = [*data.get('meta', []), ' '.join(temp_meta)]
                        temp_meta = []
                else:
                    if square_brace_count != 0:
                        temp_meta.append(span.text)
                    data['meanings'] = [*data.get('meanings', []), span.text]
            words_meanings[word] = data
    return words_meanings


def main():
    if len(sys.argv) < 2:
        print('Using default directory "tmp/chunks". To provide custom directory, pass it as argument.')
        html_chunks_dir = 'tmp/chunks'
    else:
        html_chunks_dir = sys.argv[1]

    words_dict = {}

    filenames = [x for x in os.listdir(html_chunks_dir) if x[-5:] == '.html']
    total = len(filenames)

    for i, filename in enumerate(filenames):
        filepath = os.path.join(html_chunks_dir, filename)
        print('Processing..', filepath, ' '*5, f'{i+1} of {total}')
        words_dict.update(parse_words(open(filepath).read()))
    print('Writing to json file data/words_meanings.json')
    with open('data/words_meanings.json', 'w') as f:
        json.dump(words_dict, f, indent=2)
    print('Done')

    print('Writing just words to data/just_words.txt')
    with open('data/just_words.txt', 'w') as f:
        [f.write(f'{x}\n') for x in words_dict.keys()]
    print('Done')


def test():
    words_meanings = parse_words(open('tmp/chunks/00001.html').read())
    print('  '.join(words_meanings.keys()))


if __name__ == '__main__':
    main()
