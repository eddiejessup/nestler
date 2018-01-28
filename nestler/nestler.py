import logging
import argparse
import os.path as opath

from . import parseful as parse
from .constants import ChunkOption
from . import output_routines
from . import start_zmq_kernel

logger = logging.getLogger(__name__)


DEFAULT_CHUNK_OPTS = {
    ChunkOption.label: None,
    ChunkOption.do_cache: False,
    ChunkOption.cache_path: 'cache/',
    ChunkOption.chunk_dependencies: None,
    ChunkOption.child_files: None,
    ChunkOption.engine: 'python',
    ChunkOption.run_code: True,
    ChunkOption.show_code_and_results: True,
    ChunkOption.show_code: True,
    ChunkOption.do_syntax_highlighting: True,
    ChunkOption.do_tidy: False,
    ChunkOption.show_errors: False,
    ChunkOption.show_warnings: True,
    ChunkOption.show_messages: True,
    ChunkOption.result_prefix: '>',
    ChunkOption.collapse_results: False,
    ChunkOption.results_style: 'markup',
    ChunkOption.figure_alignment: 'default',
    ChunkOption.figure_caption: None,
    ChunkOption.figure_height: None,
    ChunkOption.figure_width: None,
}


def run(in_stream, out_path_base, connection_file=None):
    connection_file = start_zmq_kernel.CONNECTION_FILE
    logger.info('Reading file...')
    md_in = in_stream.read()
    logger.info('Read file.')

    logger.info('Parsing file...')
    header, parts = parse.parse(md_in)
    logger.info('Parsed file.')

    default_options = DEFAULT_CHUNK_OPTS.copy()
    # TODO.
    global_options = default_options.copy()

    for output_fmt_str in header.get('output', {}):
        logger.info(f'Rendering file to "{output_fmt_str}"...')
        output_fmt = output_routines.OutputFormat(output_fmt_str)
        output_routine = output_routines.FORMAT_TO_ROUTINE[output_fmt]
        output_routine(header, parts, output_fmt_str, global_options,
                       out_path_base,
                       connection_file=connection_file)
        logger.info(f'Rendered file to "{output_fmt_str}".')


def set_log_level(verbose_count):
    # Set log level to WARN for 1, then increase verbosity with each increment.
    level = max(3 - verbose_count, 0) * 10
    logging.basicConfig(level=level)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        'in_file',
        type=argparse.FileType('r'),
        # This is my preferred name for 'usage' purposes, but I can't use it
        # internally as it's a keyword.
        metavar='input'
    )
    parser.add_argument('-e', '--existing',
                        help='Kernel connection file.')
    parser.add_argument('-v', '--verbose', dest='verbose_count',
                        action='count', default=0,
                        help='Each occurrence increases log verbosity.')
    args = parser.parse_args()

    set_log_level(args.verbose_count)

    logging.basicConfig(level=logging.INFO)
    out_path_base = opath.splitext(args.in_file.name)[0]
    run(args.in_file, out_path_base,
        connection_file=args.existing)
