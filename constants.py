from enum import Enum


class ResultsStyle(Enum):
    markup = 'markup'
    as_is = 'asis'
    hide = 'hide'
    hold = 'hold'


class ChunkOption(Enum):
    label = 'label'
    # Whether to cache results for future knits.
    do_cache = 'cache'
    # Directory in which to save cached results.
    cache_path = 'cache.path'
    # Chunk dependencies, used for caching.
    chunk_dependencies = 'dependson'
    # Files to knit then include.
    child_files = 'child'
    # Programming language used.
    engine = 'engine'
    # Whether to run the code.
    run_code = 'eval'
    # Whether to show the code and results.
    show_code_and_results = 'include'
    # Whether to show the code.
    show_code = 'echo'
    # Whether to highlight the code.
    do_syntax_highlighting = 'highlight'
    # Whether to tidy the code before showing it.
    do_tidy = 'tidy'
    # Whether to show error messages. Otherwise, stop the render on errors.
    show_errors = 'error'
    # Whether to show code warnings.
    show_warnings = 'warning'
    # Whether to show code messages.
    show_messages = 'message'
    # Prefix for each line of results.
    result_prefix = 'comment'
    # Whether to collapse all results into a single block.
    collapse_results = 'collapse'
    # How to show results:
    # - 'asis': Pass results through.
    # - 'hide': Do not show results.
    # - 'hold': Put all results below all code.
    # - 'markup': Present in the usual way.
    results_style = 'results'
    # How to align figures: 'left', 'right', 'center', or 'default'.
    figure_alignment = 'fig.align'
    figure_caption = 'fig.cap'
    # Figure dimensions, in inches.
    figure_height = 'fig.height'
    figure_width = 'fig.width'
