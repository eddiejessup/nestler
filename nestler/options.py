from decimal import Decimal

from . import parseful as parse
from .constants import ChunkOption, ResultsStyle


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


def coerce_val_to_str(value_raw):
    if isinstance(value_raw, parse.StringLit):
        return value_raw.contents
    elif isinstance(value_raw, parse.Identifier):
        return value_raw.name
    else:
        raise ValueError(value_raw)


def coerce_val_to_boolean(value_raw):
    try:
        val_str = coerce_val_to_str(value_raw)
    except ValueError:
        if isinstance(value_raw, Decimal):
            return bool(value_raw)
        else:
            raise
    else:
        val_str = val_str.lower().strip()
        if val_str in ('true', '1', 'yes', 'y', 'on'):
            return True
        elif val_str in ('false', '0', 'no', 'n', 'off'):
            return False
        elif val_str in ('none', 'null', 'na'):
            return None
        else:
            raise ValueError(value_raw)


def update_chunk_options(initial_options, new_options):
    opts = initial_options.copy()
    for opt_str, value_raw in new_options.items():
        chunk_opt = ChunkOption(opt_str)
        if chunk_opt == ChunkOption.result_prefix:
            if not isinstance(value_raw, parse.StringLit):
                raise Exception
            else:
                value = value_raw.contents
        elif chunk_opt in BOOLEAN_CHUNK_OPTS:
            value = coerce_val_to_boolean(value_raw)
        elif chunk_opt == ChunkOption.results_style:
            val_str = coerce_val_to_str(value_raw)
            value = ResultsStyle(val_str)
        elif chunk_opt == ChunkOption.label:
            value = value_raw
        else:
            import pdb; pdb.set_trace()
            raise NotImplementedError((opt_str, value_raw))
        opts[chunk_opt] = value
    return opts
