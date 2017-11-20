from pprint import pprint as pp
from queue import Empty
import logging

from jupyter_client import KernelManager

import parseful as parse

logger = logging.getLogger(__name__)


def exec_code(client, code):
    exec_msg_id = client.execute(code)
    exec_reply = client.get_shell_msg(exec_msg_id)
    replies = []
    while True:
        try:
            io_reply = client.get_iopub_msg(timeout=2)
        except Empty:
            logger.info('All messages received')
            break
        c = io_reply['content']
        msg_type = io_reply['msg_type']
        if msg_type == 'stream':
            replies.append(io_reply)
        elif msg_type == 'execute_input':
            logger.debug(f"Everyone, everyone! We are executing this:")
            logger.debug('```', end='')
            logger.debug(c['code'], end='')
            logger.debug('```')
        elif msg_type in ('execute_result', 'display_data'):
            replies.append(io_reply)
        elif msg_type == 'status':
            status = c['execution_state']
            logger.info(f"Kernel is '{status}'")
            if status == 'idle':
                if replies:
                    break
        elif msg_type == 'error':
            ename = c['ename']
            evalue = c['evalue']
            sexc = f"{ename}: {evalue}"
            logger.error(f"Exception: '{sexc}'")
            raise ValueError(f"Got exception: '{sexc}'")
        else:
            pp(io_reply)
            raise NotImplementedError
    return replies


def render_inline(code, replies):
    s = ''
    for reply in replies:
        if reply['msg_type'] == 'execute_result':
            data = reply[u"content"][u'data']
            for data_type, datum in data.items():
                if data_type == 'text/plain':
                    s += datum
                else:
                    import pdb; pdb.set_trace()
                    raise NotImplementedError
        else:
            raise NotImplementedError
    return s


def render_chunk(code, options, replies):
    sects = [f"```\n{code}```"]
    for reply in replies:
        if reply['msg_type'] in ('execute_result', 'display_data'):
            data = reply[u"content"][u'data']
            for datum_type, datum in data.items():
                if datum_type == 'text/plain':
                    lines = datum.strip().split('\n')
                    lines_prompt = [f"> {ln}" for ln in lines]
                    out = '\n'.join(lines_prompt)
                    sects.append(out)
                elif datum_type == 'text/html':
                    sects.append(datum)
                elif datum_type == 'image/png':
                    data_uri = f"data:{datum_type};base64,{datum}"
                    el = f'<img src="{data_uri}">'
                    sects.append(el)
                else:
                    raise NotImplementedError
        elif reply['msg_type'] == 'stream':
            txt = reply['content']['text'].strip()
            sects.append(f"'{txt}'")
        else:
            raise NotImplementedError
    s = '\n\n'.join(sects) + '\n\n'
    return s


def get_kernel_client():
    manager = KernelManager()
    manager.start_kernel()
    client = manager.client()
    client.start_channels()
    # client.wait_for_ready()
    return client


def process_txt(s):
    client = get_kernel_client()

    header, parts = parse.parse(s)

    parts_evaled = []
    for part in parts:
        if isinstance(part, (parse.CodeChunk, parse.InlineCode)):
            replies = exec_code(client, part.code)
            if isinstance(part, parse.InlineCode):
                r = render_inline(part.code, replies)
            elif isinstance(part, parse.CodeChunk):
                r = render_chunk(part.code, part.options, replies)
            else:
                raise Exception
        elif isinstance(part, str):
            r = part
        else:
            raise Exception
        parts_evaled.append(r)
    client.shutdown()
    s = ''.join(parts_evaled)
    return s


def test_pandas_html():
    client = get_kernel_client()
    code = '''
import pandas as pd
d = pd.DataFrame([1])
d
    '''
    replies = exec_code(client, code)
    for r in replies:
        pp(r)
        print()

    s = render_chunk(code, [], replies)
    pp(s)

    return


def test_integrated():
    txt_in = open('in.md').read()
    txt_out = process_txt(txt_in)
    print(txt_out)


def test_img():
    client = get_kernel_client()
    code = '''
import matplotlib.pyplot as plt
plt.plot([1, 1],[2, 2])
plt.show()
print('hello')
    '''
    replies = exec_code(client, code)
    # for r in replies:
    #     pp(r)
    #     print()

    s = render_chunk(code, [], replies)
    # pp(s)
    return


if __name__ == '__main__':
    test_integrated()
    # test_pandas_html()
    # test_img()
