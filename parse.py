from decimal import Decimal
from collections import namedtuple, OrderedDict

import pyparsing as pp

pp.ParserElement.setDefaultWhitespaceChars('')

StringLit = namedtuple('StringLit', ['contents'])
Identifier = namedtuple('Identifier', ['name'])

Text = namedtuple('Text', ['contents'])
CodeChunk = namedtuple('CodeChunk', ['code', 'options'])
InlineCode = namedtuple('InlineCode', ['code'])

WTF_CHAR = '§'
# Python-style identifier, but with optional dot separators in rest for cases like `fig.cap = "..."`
identifier = pp.Word(initChars=pp.alphas+"_", bodyChars=pp.alphanums+"_.").setParseAction(lambda t: Identifier(name=t[0]))

# Define a few characters involved in rules.
TICK, L_BRACE, R_BRACE, EQUALS, P, NL, WTF = (
    map(pp.Suppress, '`{}=p\n' + WTF_CHAR)
)
# TRIPLE_TICK = pp.Suppress(pp.Literal('```'))

number_literal = (
    pp.Combine(pp.Word("+-" + pp.nums, pp.nums) + pp.Optional(pp.Literal(".") + pp.Optional(pp.Word(pp.nums))))
    .setParseAction(lambda t: Decimal(t[0]))
)

string_literal = pp.quotedString.setParseAction(lambda t: StringLit(contents=t[0][1:-1]))

OPT_WHITE_CHARS = ' \t\r\n'
whitespace = pp.Suppress(pp.White(ws=OPT_WHITE_CHARS))
line_end = pp.Suppress(pp.LineEnd())
maybe_whitespace = pp.Suppress(pp.Optional(pp.White(ws=OPT_WHITE_CHARS)))

# Identifier is just there because values can be set to FALSE, like it's an
# identifier. Maybe it is, I don't know how R works.
option_val = identifier | string_literal | number_literal
chunk_option = (identifier + maybe_whitespace + EQUALS + maybe_whitespace + option_val).setParseAction(tuple)

chunk_options_body = (whitespace + pp.delimitedList(chunk_option, delim=',')).setParseAction(lambda t: OrderedDict((ident.name, val) for ident, val in t.asList()))
chunk_header = L_BRACE + P + pp.Optional(chunk_options_body, default={}) + maybe_whitespace + R_BRACE
VALID_CODE_CHARS = (pp.printables + '\n\r\t ').replace(WTF_CHAR, '')
code_chunk_body = pp.Word(VALID_CODE_CHARS).setParseAction(lambda t: t[0])
code_chunk = (NL + WTF + chunk_header + code_chunk_body + WTF).setParseAction(lambda t: CodeChunk(code=t[1], options=t[0]))
code_chunk_text = (WTF + code_chunk_body + WTF).setParseAction(lambda t: '```' + t[0] + '```\n')

VALID_INLINE_CHARS = (pp.printables + '\t ').replace('`', '')
inline_code_body = pp.Word(VALID_INLINE_CHARS).setParseAction(lambda t: t[0])
inline_code_head = (P + whitespace).setParseAction(lambda t: True)
inline_code = (TICK + inline_code_head + inline_code_body + TICK).setParseAction(lambda t: InlineCode(code=t[1]))
inline_text = (TICK + inline_code_body + TICK).setParseAction(lambda t: '`' + t[0] + '` ')

VALID_TEXT_CHARS = (pp.printables + '\n\r\t ').replace('`', '')
plain_text = pp.Word(VALID_TEXT_CHARS).setParseAction(lambda t: t[0])

text = (inline_text | code_chunk_text | plain_text).setParseAction(lambda t: Text(t[0]))
doc = pp.ZeroOrMore(code_chunk | inline_code | text)


def parse(s):
    s = s.replace('```', WTF_CHAR)
    try:
        return doc.parseString(s, parseAll=True)
    except (pp.ParseFatalException, pp.ParseException) as e:
        print("Error:" + e.msg)
        print(e.markInputline('^'))
        raise


if __name__ == '__main__':
    s = '''
    # Hello the `p blues`

    ```
    print("hi")
    print(1)
    ```

    ```{p a=2}
    print("hi`")
    print(1)
    ```

    hi `guys` you do maaaaaaaaaan
    '''
    s = open('in.md').read()
    # print(s)
    res = parse(s)

    for part in res:
        print(part)
