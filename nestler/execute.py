from queue import Empty
import logging

from jupyter_client import KernelManager

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10


def exec_code(client, code, raise_errors):
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
            logger.debug(f"Executing:\n```\n{c['code']}```")
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
            if raise_errors:
                sexc = recover_exception(reply)
                raise ValueError(f"Got exception: '{sexc}'")
            else:
                replies.append(reply)
        else:
            raise NotImplementedError(reply)
    return replies


def recover_exception(reply):
    c = reply['content']
    ename = c['ename']
    evalue = c['evalue']
    sexc = f"{ename}: {evalue}"
    return sexc


def get_kernel_client():
    manager = KernelManager()
    manager.start_kernel()
    client = manager.client()
    client.start_channels()
    # client.wait_for_ready()
    return client
