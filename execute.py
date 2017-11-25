from queue import Empty
import logging

from jupyter_client import KernelManager

logger = logging.getLogger(__name__)


def exec_code(client, code, raise_errors):
    client.execute(code)
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
            logger.debug(f"Everyone, everyone! We are executing this:\n```\nc['code']\n```")
        elif msg_type in ('execute_result', 'display_data'):
            replies.append(io_reply)
        elif msg_type == 'status':
            status = c['execution_state']
            logger.info(f"Kernel is '{status}'")
            if status == 'idle':
                if replies:
                    break
        elif msg_type == 'error':
            if raise_errors:
                sexc = recover_exception(io_reply)
                raise ValueError(f"Got exception: '{sexc}'")
            else:
                replies.append(io_reply)
        else:
            raise NotImplementedError
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
