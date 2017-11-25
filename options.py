from decimal import Decimal

import parseful as parse
from constants import ChunkOption, ResultsStyle


BOOLEAN_CHUNK_OPTS = (
    ChunkOption.do_cache,
    ChunkOption.run_code,
    ChunkOption.show_code_and_results,
    ChunkOption.show_code,
    ChunkOption.do_syntax_highlighting,
    ChunkOption.do_tidy,
    ChunkOption.show_errors,
    ChunkOption.show_warnings,
    ChunkOption.show_messages,
    ChunkOption.collapse_results,
)


def coerce_val_to_str(val_raw):
    if isinstance(val_raw, parse.StringLit):
        return val_raw.contents
    elif isinstance(val_raw, parse.Identifier):
        return val_raw.name
    else:
        raise ValueError(val_raw)


def coerce_val_to_boolean(val_raw):
    try:
        val_str = coerce_val_to_str(val_raw)
    except ValueError:
        if isinstance(val_raw, Decimal):
            return bool(val_raw)
        else:
            raise
    else:
        val_str = val_str.lower().strip()
        if val_str in ('true', 't', '1'):
            return True
        elif val_str in ('false', 'f', '0'):
            return False
        elif val_str in ('none', 'null', 'na'):
            return None
        else:
            raise ValueError(val_raw)


def update_chunk_options(initial_options, new_options):
    opts = initial_options.copy()
    for opt_str, val_raw in new_options.items():
        chunk_opt = ChunkOption(opt_str)
        if chunk_opt == ChunkOption.result_prefix:
            if not isinstance(val_raw, parse.StringLit):
                raise Exception
            else:
                value = val_raw.contents
        elif chunk_opt in BOOLEAN_CHUNK_OPTS:
            value = coerce_val_to_boolean(val_raw)
        elif chunk_opt == ChunkOption.results_style:
            style_val = coerce_val_to_str(val_raw)
            value = ResultsStyle(style_val)
        else:
            import pdb; pdb.set_trace()
            raise NotImplementedError((opt_str, val_raw))
        opts[chunk_opt] = value
    return opts
