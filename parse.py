from decimal import Decimal
from collections import namedtuple, OrderedDict

import pyparsing as pp

StringLit = namedtuple('StringLit', ['contents'])
Identifier = namedtuple('Identifier', ['name'])

Text = namedtuple('Text', ['contents'])
CodeChunk = namedtuple('CodeChunk', ['options', 'code'])
InlineCode = namedtuple('InlineCode', ['code'])

# Python-style identifier, but with optional dot separators in rest for cases like `fig.cap = "..."`
identifier = pp.Word(initChars=pp.alphas+"_", bodyChars=pp.alphanums+"_.").setParseAction(lambda t: Identifier(name=t[0]))

# Define a few characters involved in rules.
TICK, L_BRACE, R_BRACE, EQUALS, P = (
    map(pp.Suppress, '`{}=p')
)
TRIPLE_TICK = pp.Suppress(pp.Literal('```'))

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
chunk_options = L_BRACE + P + pp.Optional(chunk_options_body, default={}) + maybe_whitespace + R_BRACE
VALID_CODE_CHARS = (pp.printables + '\n\r\t ').replace('`', '')
chunk_code = pp.Word(VALID_CODE_CHARS).setParseAction(lambda t: t[0])
chunk = (TRIPLE_TICK + chunk_options + line_end + chunk_code + TRIPLE_TICK).setParseAction(lambda t: CodeChunk(options=t[0], code=t[1]))

VALID_INLINE_CHARS = (pp.printables + '\t ').replace('`', '')
inline_code = pp.Word(VALID_INLINE_CHARS).setParseAction(lambda t: t[0])
inline = (TICK + P + whitespace + inline_code + TICK).setParseAction(lambda t: InlineCode(code=t[0]))

VALID_TEXT_CHARS = (pp.printables + '\n\r\t ').replace('`', '')
text = pp.Word(VALID_TEXT_CHARS).setParseAction(lambda t: Text(contents=t[0]))

doc = pp.ZeroOrMore(chunk | inline | text)


def parse(s):
    try:
        return doc.parseString(s, parseAll=True)
    except (pp.ParseFatalException, pp.ParseException) as e:
        print("Error:" + e.msg)
        print(e.markInputline('^'))
        raise


if __name__ == '__main__':
    res = (doc.parseString('''
    # Hello the

    ```{p a=2.1, b=TRUE}
    print("hi")
    print(1)
    ```

    # Hi chums

    Here are `p a``p b` chunks of code:

    ```{p a=2.1, b=TRUE}
    print("hi")
    print(1)
    ```

    The end.
    ''', parseAll=True))

    for part in res:
        print(part)
