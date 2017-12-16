import logging
import argparse
import os.path as opath

from . import parseful as parse
from .constants import ChunkOption
from . import output_routines

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


def main(in_stream, out_path_base):
    md_in = in_stream.read()

    header, parts = parse.parse(md_in)

    default_options = DEFAULT_CHUNK_OPTS.copy()
    # TODO.
    global_options = default_options.copy()

    for output_fmt_str in header.get('output', {}):
        output_fmt = output_routines.OutputFormat(output_fmt_str)
        output_routine = output_routines.FORMAT_TO_ROUTINE[output_fmt]
        output_routine(header, parts, output_fmt_str, global_options,
                       out_path_base)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        'in_file',
        type=argparse.FileType('r'),
        # This is my preferred name for 'usage' purposes, but I can't use it
        # internally as it's a keyword.
        metavar='input'
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    out_path_base = opath.splitext(args.in_file.name)[0]
    main(args.in_file, out_path_base)
