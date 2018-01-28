from ipykernel.kernelapp import IPKernelApp

CONNECTION_FILE = '/var/folders/gw/90gtwfsd7696yywgwr5xw1kszj41zb/T/tmp01lhp83r.json'

if __name__ == '__main__':
    app = IPKernelApp.launch_instance(
        connection_file=CONNECTION_FILE,
        # Don't handle stdout, stderr specially, to let us keep using PDB.
        outstream_class='outs.dummy_out_stream',
    )
