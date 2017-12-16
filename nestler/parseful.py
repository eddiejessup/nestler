import re
from decimal import Decimal
from collections import namedtuple, OrderedDict

import yaml
import pyparsing as pp

CODE_PREFIX_STR = 'py'

StringLit = namedtuple('StringLit', ['contents'])
Identifier = namedtuple('Identifier', ['name'])

ChunkAssignOpt = namedtuple('ChunkAssignOpt', ['identifier', 'value'])

CodeChunk = namedtuple('CodeChunk', ['code', 'options'])
InlineCode = namedtuple('InlineCode', ['code'])

# Python-style identifier, but with optional dot separators in rest for cases
# like `fig.cap = "..."`
identifier = (pp.Word(initChars=pp.alphas+"_", bodyChars=pp.alphanums+"_.")
              .setParseAction(lambda t: Identifier(name=t[0])))

# Define a few characters involved in rules.
L_BRACE, R_BRACE, EQUALS = map(pp.Suppress, '{}=')
CODE_PREFIX = pp.Suppress(pp.Literal(CODE_PREFIX_STR))

number_literal = (
    pp.Combine(
        pp.Word("+-" + pp.nums, pp.nums)
        + pp.Optional(pp.Literal(".") + pp.Optional(pp.Word(pp.nums)))
    ).setParseAction(lambda t: Decimal(t[0]))
)

string_literal = (pp.quotedString
                  .setParseAction(lambda t: StringLit(contents=t[0][1:-1])))

WHITE_CHARS = ' \t\r\n'
whitespace = pp.Suppress(pp.White(ws=WHITE_CHARS))
maybe_whitespace = pp.Suppress(pp.Optional(pp.White(ws=WHITE_CHARS)))


def process_chunk_opts(t):
    r = OrderedDict()
    for opt in t.asList():
        if isinstance(opt, ChunkAssignOpt):
            ident, val = opt
            r[ident.name] = val
        elif isinstance(opt, Identifier):
            r['label'] = opt.name
        elif isinstance(opt, StringLit):
            r[opt.contents] = None
        else:
            raise Exception
    return r


# Identifier is just there because values can be set to FALSE, like it's an
# identifier. Maybe it is, I don't know how R works.
option_val = identifier | string_literal | number_literal
chunk_assign_option = (
    identifier + maybe_whitespace + EQUALS + maybe_whitespace + option_val
).setParseAction(lambda t: ChunkAssignOpt(identifier=t[0], value=t[1]))
chunk_options = (
    whitespace
    + pp.delimitedList(chunk_assign_option | identifier | string_literal,
                       delim=',')
).setParseAction(process_chunk_opts)
chunk_header = (
    L_BRACE + CODE_PREFIX
    # + pp.Optional(chunk_label, default=None)
    + pp.Optional(chunk_options, default={})
    + maybe_whitespace + R_BRACE
)
VALID_CODE_CHARS = (pp.printables + '\n\r\t ')
code_body = pp.Word(VALID_CODE_CHARS).setParseAction(lambda t: t[0])

chunk = (
    chunk_header + code_body
).setParseAction(lambda t: CodeChunk(options=t[0], code=t[1]))

inline_code = (
    CODE_PREFIX + whitespace + code_body
).setParseAction(lambda t: InlineCode(code=t[0]))

VALID_TEXT_CHARS = (pp.printables + '\n\r\t ')


def read_maybe_yaml_block(source):
    match = re.match(r'^---\n([\s\S]+?)\n---', source)
    if match is not None:
        yaml_source = match.group(1)
        contents = yaml.safe_load(yaml_source)
        remainder = source[match.end():]
    else:
        contents = {}
        remainder = source
    return contents, remainder


CHUNK_PREFIX = '\n```'
CHUNK_PARSE_START = CHUNK_PREFIX + '{' + CODE_PREFIX_STR
CHUNK_PARSE_END = '```'
INLINE_PREFIX = '`'
INLINE_PARSE_START = f'{INLINE_PREFIX}{CODE_PREFIX_STR} '
INLINE_PARSE_END = '`'


def _parse(s):
    header, s = read_maybe_yaml_block(s)

    i = 0
    parts = []
    while i < len(s):
        if s[i:].startswith(CHUNK_PARSE_START):
            i += len(CHUNK_PREFIX)
            chunk_str = ''
            while not s[i:].startswith(CHUNK_PARSE_END):
                chunk_str += s[i]
                i += 1
            i += len(CHUNK_PARSE_END)
            chunk_obj = chunk.parseString(chunk_str, parseAll=True)
            parts.extend(chunk_obj)
        elif s[i:].startswith(INLINE_PARSE_START):
            i += len(INLINE_PREFIX)
            inline_code_str = ''
            while not s[i:].startswith(INLINE_PARSE_END):
                inline_code_str += s[i]
                i += 1
            i += len(INLINE_PARSE_END)
            inline_code_obj = inline_code.parseString(inline_code_str,
                                                      parseAll=True)
            parts.extend(inline_code_obj)
        else:
            c = s[i]
            if (len(parts) == 0) or (not isinstance(parts[-1], str)):
                parts.append(c)
            else:
                parts[-1] += c
            i += 1
    return header, parts


def parse(s):
    try:
        return _parse(s)
    except (pp.ParseFatalException, pp.ParseException) as e:
        print("Error:" + e.msg)
        print(e.markInputline('^'))
        raise


if __name__ == '__main__':
    s = '''
---
a: 2
---

# Hello the `py blues`

```{py lab, "yo", a=2}
print("hi`")
print(1)
```

hi `guys` you do maaaaaaaaaan

```{py withLabel}
print(1)
```

```{py withLabel11, b3 = 3}
print(1)
```
'''.strip()
    # s = open('in.md').read()
    header, parts = parse(s)
    for p in parts:
        print(p)
    print(header)
