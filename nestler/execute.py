from queue import Empty
import logging
from collections import namedtuple

from jupyter_client import KernelManager, BlockingKernelClient

from . import comms

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 2


def exec_code_to_replies(client, code, implicit_display):
    interactivity = 'last_expr' if implicit_display else 'none'
    comms.set_interactivity(client, interactivity)

    client.execute(code)
    replies = []
    while True:
        try:
            reply = client.get_iopub_msg(timeout=TIMEOUT_SECONDS)
        except Empty:
            logger.info('All messages received')
            break
        c = reply['content']
        msg_type = reply['msg_type']
        if msg_type == 'stream':
            logger.debug(f"Got {msg_type} reply: '{c}'")
            replies.append(reply)
        elif msg_type == 'execute_input':
            logger.debug(f"Executing:\n```\n{c['code']}\n```")
        elif msg_type in ('execute_result', 'display_data'):
            logger.debug(f"Got {msg_type} reply: '{c}'")
            replies.append(reply)
        elif msg_type == 'status':
            status = c['execution_state']
            logger.info(f"Kernel is '{status}'")
            if status == 'idle':
                if replies:
                    break
        elif msg_type == 'error':
            replies.append(reply)
        else:
            raise NotImplementedError(reply)
    return replies


ExecOutput = namedtuple('ExecOutput', 'kind content')


def interpret_replies(replies):
    outs = {}
    for reply in replies:
        msg_type = reply['msg_type']
        if reply['metadata']:
            import pdb; pdb.set_trace()
        if msg_type in ('execute_result', 'display_data'):
            data = reply[u'content'][u'data']
            for datum_type, datum in data.items():
                if datum_type == 'text/plain':
                    if msg_type == 'display_data':
                        kind = 'display_text'
                    else:
                        kind = 'text'
                    outs.setdefault(kind, []).append(
                        datum.strip("'")
                    )
                elif datum_type == 'text/html':
                    outs.setdefault('html', []).append(
                        datum
                    )
                elif datum_type == 'image/png':
                    outs.setdefault('image', []).append(
                        {
                            'format': datum_type,
                            'data': datum,
                            'slug': None,
                            'caption': None,
                        },
                    )
                elif datum_type == 'application/javascript':
                    outs.setdefault('script', []).append(
                        datum,
                    )
                elif datum_type == 'application/vnd.bokehjs_load.v0+json':
                    outs.setdefault('script', []).append(
                        datum,
                    )
                elif datum_type == 'application/json':
                    if datum.get('kind') == 'caption':
                        outs.setdefault('caption', []).append(
                            datum
                        )
                    else:
                        raise NotImplementedError(datum)
                else:
                    raise NotImplementedError(datum_type)
        elif msg_type == 'stream':
            txt = reply['content']['text'].rstrip()
            stream_name = reply['content']['name']
            outs.setdefault(stream_name, []).append(
                txt,
            )
        elif msg_type == 'error':
            c = reply['content']
            outs.setdefault('error', []).append(
                {
                    'name': c['ename'],
                    'value': c['evalue'],
                },
            )
        else:
            raise NotImplementedError(msg_type)
    for out, cap in zip(outs.get('image', []), outs.get('caption', [])):
        out['slug'] = cap['slug']
        out['caption'] = cap['caption']
    outs.pop('caption', None)
    return outs


def exec_code(client, code, implicit_display):
    replies = exec_code_to_replies(client, code, implicit_display)
    outs = interpret_replies(replies)
    return outs

def recover_exception(out):
    sexc = f"{out['name']}: {out['value']}"
    return sexc


def get_kernel_client(connection_file=None):
    if connection_file is None:
        manager = KernelManager()
        manager.start_kernel()
        client = manager.client()
    else:
        client = BlockingKernelClient(connection_file=connection_file)
        client.load_connection_file()
    client.start_channels()

    # Open the new-comm comm handler.
    comms.open_register_target_comm(client)
    comms.open_interactivity_comm(client)

    return client
