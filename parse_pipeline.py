from typing import Tuple, List

from bs4 import BeautifulSoup

from convert import preeti_to_unicode


# typings
Token = Tuple[str, str]

PREETI = 'PREETI'
HIMALAYA = 'HIMALAYA'
TIMESNEWROMAN = 'TIMESNEWROMAN'

FONT_FAMILIES_TOKEN_MAPPING = {
    'EABPMI+Preeti': PREETI,
    'AICLBD+Himalayabold': HIMALAYA,
    'EABPNM+Himalayabold': HIMALAYA,
    'AICLFF+TimesNewRoman': TIMESNEWROMAN,
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
    3. Replace “ by F
    """
    return preeti.replace('®', '/').replace('\n', ' ').replace('“', 'F')


def is_himalaya(token: Token) -> bool:
    font, _ = token
    return font == HIMALAYA


def convert(token: Token):
    font, txt = token
    assert '\n' not in txt, 'newline found in ' + txt
    if font in (PREETI, HIMALAYA):
        return preeti_to_unicode(txt)
    return txt


def files_reader(next_pipeline, files_count=1400):
    for file_number in range(0, files_count):
        name = f'tmp/chunks/{str(file_number).zfill(5)}.html'
        try:
            html_content = open(name).read()
            next_pipeline.send(html_content)
        except FileNotFoundError:
            break
    next_pipeline.close()


def html_to_blocks(next_pipeline):
    while True:
        html = (yield)
        soup = BeautifulSoup(html, 'html5lib')
        divs = soup.findAll('div')

        for div in divs:
            block: List[Tuple[str, str]] = []
            for span in div.findAll('span'):
                token = get_token_for_span(span)

                # NOTE: the following needs to be hardcoded, it's embedded in the pdf
                if token is None or 'correction' in span.text or 'yakkha' in span.text:
                    continue

                txt = preprocess_text(span.text)
                txt = txt.replace('\n', '')
                token_data = (token, txt)

                # If previous token has same font, just concat them
                if block and block[-1][0] == token:
                    _, last_txt = block.pop()
                    last_txt += f'{txt}'
                    token_data = (token, last_txt)

                block.append(token_data)
            next_pipeline.send(block)


def block_parser(next_pipeline):
    try:
        while True:
            block = (yield)
            # Filter out empty items
            block = [x for x in block if x]
            if not block:
                continue
            # block is continuity if first item is preeeti, NOTE: this is crude
            is_previous = not is_himalaya(block[0])
            next_pipeline.send((block, is_previous))
    except GeneratorExit:
        print('Done: block_parser')


def accumulator(next_pipeline):
    """
    This gets block data from previous pipeline. But it might happen that a new
    block obtained might be continuation of another block, so, write only when
    """
    previous = []
    while True:
        (data, is_previous) = (yield)

        if not is_previous:
            # TODO: fix when to write
            print('sent ************************************************')
            print(previous)
            print('*****************************************************')
            next_pipeline.send(previous)
            previous = data
        else:
            previous.extend(data)

    next_pipeline.send(previous)


def file_writer():
    try:
        with open('test.txt', 'w') as writefile:
            while True:
                data = (yield)
                converted = ''.join([convert(x) for x in data])
                writefile.write(converted)
                writefile.write('\n')
    except GeneratorExit:
        print('Done writing')


def main():
    """ Main function"""
    writer = file_writer()
    acc = accumulator(writer)
    blk_parser = block_parser(acc)
    html_pipeline = html_to_blocks(blk_parser)
    next(html_pipeline)
    next(blk_parser)
    next(acc)
    next(writer)
    files_reader(next_pipeline=html_pipeline, files_count=2)


if __name__ == '__main__':
    main()
