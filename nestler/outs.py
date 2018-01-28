import sys


def catchy_handler(func):
    def handle(*args, **kwargs):
        # import pdb; pdb.set_trace()
        return func(*args, **kwargs)
    return handle


def dummy_out_stream(session, thread, stream_name):
    if stream_name == 'stdout':
        return sys.stdout
        # return catchy_handler(sys.stdout)
    elif stream_name == 'stderr':
        return sys.stderr
        # return catchy_handler(sys.stderr)
    else:
        raise ValueError('Unknown stream type')
