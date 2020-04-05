#!/bin/python
"""
This module contains functions that parse the words and meanings text
"""

import sys
import re

from bs4 import BeautifulSoup


FONT_FAMILIES_TOKEN_MAPPING = {
    # 'EABPNK+FONTASYHIMALITTNORMAL': 'HIMALITT',  # Ignore this as this only serves for page number
    'EABPMI+Preeti': 'PREETI',
    'AICLBD+Himalayabold': 'HIMALAYA',
    'AICLFF+TimesNewRoman': 'TIMESNEWROMAN',
}

# This is just a dummy substitution for times new roman font in order to prevent them
# from being translated by the unicode converter
TIMESNEWROMAN_MAP = {
    '[': 'Ψ',
    ']': 'Φ',
    '~': 'Π',
    '>': 'Λ',
    '<': 'ν',
    '(': '˂',
    ')': '˃',
    ' ': ' ',
    '\n': ' ',
}

def get_token_for_span(span):
    for k, v in FONT_FAMILIES_TOKEN_MAPPING.items():
        if k in span['style']:
            return v
    return None


def preprocess_text(preeti):
    """
    1. Replace ® by equivalent for "ra" in preeti which is "/"
    2. Replace \n by space
    """
    return preeti.replace('®', '/').replace('\n', ' ')


def process_timesnewroman(txt):
    tnr_map = {
        '[': 'Ψ',
        ']': 'Φ',
        '~': 'Π',
        '>': 'Λ',
        '<': 'ν',
        '(': '˂',
        ')': '˃',
        ' ': ' ',
        '\n': ' ',
        'O': 'Ȏ',
        '2': 'ʅ',
        '=': 'ʭ',
        '!': 'ʲ',
        ',': 'ζ',
        '*': 'Ξ',
        'N': 'η',
        'o': 'Ϙ',
        ';': 'Ȥ',
        'S': 'Ŝ',
        'I': 'Ĩ',
    }
    try:
        return ''.join([tnr_map[x] for x in txt])
    except Exception as e:
        print('ERROREANEOUS', txt)
        raise e


def generate_fontfamily_text_list(html: str) -> [str]:
    font_mapped_list = []

    soup = BeautifulSoup(html, 'html5lib')
    divs = soup.findAll('div')

    for div in divs:
        for span in div.findAll('span'):
            token = get_token_for_span(span)
            if 'correction' in span.text or 'yakkha' in span.text:
                continue
            if token is None:
                continue
            if token == 'TIMESNEWROMAN':
                token = 'PREETI'
                txt = process_timesnewroman(span.text)
            else:
                txt = preprocess_text(span.text)

            tokenized_txt = f'{token}{txt}{token}'
            # If previous token has same font, just append them
            if font_mapped_list and token in font_mapped_list[-1]:
                last = font_mapped_list[-1]
                last = last.replace(token, '')
                last = f'{token}{last} {txt}{token}'
                font_mapped_list[-1] = last
            else:
                font_mapped_list.append(tokenized_txt)
    return font_mapped_list


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


prev_reminder_regex = '(PREETI(?P<reminder>.*?)PREETI)?'
himalaya_regex = 'HIMALAYA(?P<word>.*?)HIMALAYA'
timesnew_roman_regex = 'TIMESNEWROMAN(?P<tnr>.*?)TIMESNEWROMAN'
preeti_regex = 'PREETI(?P<meaning>.*?)PREETI'

REGEX = re.compile(f'{himalaya_regex}.*?{preeti_regex}')


def get_tokenized_text(html):
    tokenized = generate_fontfamily_text_list(html)
    return ''.join(tokenized)


def parse_html(html, regex=REGEX):
    full_tokenized_text = get_tokenized_text(html)

    reminder_pat = re.compile(f'^{prev_reminder_regex}')
    reminder_match = reminder_pat.match(full_tokenized_text)
    if reminder_match:
        span = reminder_match.span()
        full_tokenized_text = full_tokenized_text[span[1]:]

    matches = REGEX.findall(full_tokenized_text)
    return matches


def print_matches(matches):
    import convert
    p2u = convert.preeti_to_unicode
    return [(p2u(x), p2u(y)) for x, y in matches]


def get_file_content(file_number):
    name = f'tmp/chunks/{str(file_number).zfill(5)}.html'
    return open(name).read()
