import argparse

from ipykernel.kernelapp import IPKernelApp

DEFAULT_CONNECTION_FILE = '/tmp/kernel.json'


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-c', '--connection-file',
        default=DEFAULT_CONNECTION_FILE,
    )
    parser.add_argument(
        '--debug',
        default=False,
        action='store_true',
    )
    args = parser.parse_args()

    kwargs = {}
    if args.debug:
        # Don't handle stdout, stderr specially, to let us keep using PDB.
        kwargs['outstream_class'] = 'nestler.outs.dummy_out_stream'

    IPKernelApp.launch_instance(
        connection_file=args.connection_file,
        **kwargs,
    )


if __name__ == '__main__':
    main()
