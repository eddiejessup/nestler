from pprint import pprint as pp
from queue import Empty
import logging

from jupyter_client import KernelManager

import parse


km = KernelManager()

km.start_kernel()
kc = km.client()
kc.start_channels()
# kc.wait_for_ready()

logger = logging.getLogger(__name__)


def exec_code(code):
    exec_msg_id = kc.execute(code)
    exec_reply = kc.get_shell_msg(exec_msg_id)
    while True:
        try:
            io_reply = kc.get_iopub_msg(timeout=2)
        except Empty:
            logger.info('All messages received')
            break
        msg_type = io_reply['msg_type']
        if msg_type == 'stream':
            stream_reply = io_reply
            answer = stream_reply['content']['text']
            break
        elif msg_type == 'execute_input':
            logger.debug(f"Everyone, everyone! We are executing this:")
            logger.debug('```', end='')
            logger.debug(io_reply['content']['code'], end='')
            logger.debug('```')
        elif msg_type == 'execute_result':
            dat = io_reply['content']['data']
            if 'text/plain' in dat:
                answer = dat['text/plain']
            else:
                raise NotImplementedError
            break
        elif msg_type == 'status':
            status = io_reply['content']['execution_state']
            logger.info(f"Kernel is '{status}'")
        else:
            pp(io_reply)
            raise NotImplementedError
    return answer


def render_inline(code, answer):
    return answer


def render_chunk(code, options, answer):
    s = f"```{code}```\n"
    s += f"> {answer}"
    return s


txt = r'''

# A Document

## Introduction

Hi shims.

```{p}
a = 2
print("Hello")
```

## Analysis

Now for some specialness: `p a`. Oof!

```{p}
print("!!!")
```

## Conclusion

Bye shims.
'''.strip()

txt_before = txt[:]

parts = parse.parse(txt)

parts_evaled = []
for part in parts:
    if isinstance(part, (parse.CodeChunk, parse.InlineCode)):
        answer = exec_code(part.code)
        if isinstance(part, parse.InlineCode):
            r = render_inline(part.code, answer)
        elif isinstance(part, parse.CodeChunk):
            r = render_chunk(part.code, part.options, answer)
        else:
            raise Exception
    elif isinstance(part, parse.Text):
        r = part.contents
    else:
        raise Exception
    parts_evaled.append(r)


txt = ''.join(parts_evaled)

# print(f"Before:")
# print(f'"""')
# print(txt_before)
# print(f'"""')
# print()

# res = re.sub(PATTERN, render, code, flags=re.DOTALL)

# print(f"After:")
# print(f'"""')
print(txt)
# print(f'"""')

kc.shutdown()
