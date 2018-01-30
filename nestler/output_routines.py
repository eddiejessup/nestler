from enum import Enum
import logging
import os

import pypandoc
import yaml
from jinja2 import FileSystemLoader, Environment

from .constants import ChunkOption, ResultsStyle
from . import parseful as parse
from . import execute
from .options import update_chunk_options
from . import utils

THIS_FILE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


tmpl_env = Environment(
    loader=FileSystemLoader(os.path.join(THIS_FILE_DIR_PATH, 'templates')),
    trim_blocks=True,
    lstrip_blocks=True
)

figure_tmpl = tmpl_env.get_template('embedded_figure.html')
script_tmpl = tmpl_env.get_template('script.html')

logger = logging.getLogger(__name__)


class RenderOption(Enum):
    # Slides: Beamer color theme.
    slide_color_theme = "colortheme"
    # Slides: Whether to show bullets one at a time at each presenter click.
    slide_incremental_bullets = "incremental"
    # Slides: The lowest heading level that defines individual slides.
    slide_heading_level = "slide_level"
    # Slides: Whether to decrease the font size.
    smaller = "smaller"
    # Slides: Bootswatch or Beamer theme.
    slide_theme = "theme"
    # Slides: Duration of a countdown timer, in minutes, to add to the footer
    # of slides.
    slide_countdown_duration = "duration"
    # The LaTeX package to use to process citations, such as 'natbib',
    # 'biblatex', or None.
    citation_package = "citation_package"
    # Let readers to toggle the display of R code. 'none', 'hide', or 'show'.
    code_folding_style = "code_folding"
    # Path to CSS with which to style the document.
    css_path = "css"
    # Graphics device to use for figure output, such as "png".
    figure_output_device = "dev"
    # Whether to render figures with captions.
    figure_caption = "fig_caption"
    # Height and width of figures, in inches.
    figure_height = "fig_height"
    # Syntax highlighting style, such as "tango", "pygments", "kate", "zenburn"
    # or "textmate".
    syntax_highlight_style = "highlight"
    # File to insert in the document (in_header, before_body, after_body).
    include_files = "includes"
    # Whether to save a copy of any intermediate markdown file.
    keep_markdown = "keep_md"
    # Whether to save a copy of any intermediate TeX file.
    keep_tex = "keep_tex"
    # Engine to use to render latex, such as 'pdflatex', 'xelatex', 'lualatex'.
    latex_engine = "latex_engine"
    # Directory of dependency files, such as Bootstrap or MathJax.
    dependencies_dir = "lib_dir"
    # Path to a custom version of MathJax to use. May be a local path or a URL.
    mathjax_path = "mathjax"
    # Markdown extensions to use.
    markdown_extensions = "md_extensions"
    # Whether to embed dependencies into the output.
    make_self_contained = "self_contained"
    # Whether to convert straight quotes to curly, dashes to em-dashes, ... to ellipses, etc..
    format_smartly = "smart"
    # Whether to add section numbers to headers.
    number_sections = "number_sections"
    # Additional arguments to pass to Pandoc.
    pandoc_args = "pandoc_args"
    # Whether to preserve the YAML header in the final document.
    preserve_yaml = "preserve_yaml"
    # A .docx file whose styles should be copied when making .docx output.
    reference_docx = "reference_docx"
    pandoc_template_path = "template"
    # Whether to add a table of contents.
    table_of_contents = "toc"
    # The lowest level of headings to add to the table of contents.
    table_of_contents_depth = "toc_depth"
    # Whether to float the table of contents to the left of the main content.
    float_table_of_contents = "toc_float"


DEFAULT_RENDER_OPTS = {
    RenderOption.citation_package: None,
    RenderOption.code_folding_style: None,
    RenderOption.slide_color_theme: None,
    RenderOption.css_path: None,
    RenderOption.figure_output_device: 'pdf',
    RenderOption.slide_countdown_duration: None,
    RenderOption.figure_caption: None,
    RenderOption.figure_height: None,
    RenderOption.syntax_highlight_style: None,
    RenderOption.include_files: None,
    RenderOption.slide_incremental_bullets: None,
    RenderOption.keep_markdown: None,
    RenderOption.keep_tex: None,
    RenderOption.latex_engine: None,
    RenderOption.dependencies_dir: None,
    RenderOption.mathjax_path: None,
    RenderOption.markdown_extensions: None,
    RenderOption.number_sections: None,
    RenderOption.pandoc_args: None,
    RenderOption.preserve_yaml: None,
    RenderOption.reference_docx: None,
    RenderOption.make_self_contained: False,
    RenderOption.slide_heading_level: None,
    RenderOption.smaller: None,
    RenderOption.format_smartly: True,
    RenderOption.pandoc_template_path: None,
    RenderOption.slide_theme: None,
    RenderOption.table_of_contents: None,
    RenderOption.table_of_contents_depth: None,
    RenderOption.float_table_of_contents: None,
}


DEFAULT_PANDOC_MD_EXTENSIONS = [
    '+fenced_code_attributes',
    '+backtick_code_blocks',
    '+tex_math_dollars',
    '-markdown_in_html_blocks',
    '+raw_html',
    '+autolink_bare_uris',
]


DEFAULT_EXTRA_PANDOC_ARGS = [
    # Make a full HTML document with a header and a footer.
    '--standalone',
]


class OutputFormat(Enum):
    # Interactive notebooks.
    html_notebook = 'html_notebook'
    # Documents.
    html_document = 'html_document'
    pdf_document = 'pdf_document'
    word_document = 'word_document'
    odt_document = 'odt_document'
    rtf_document = 'rtf_document'
    md_document = 'md_document'
    # Presentations.
    ioslides_presentation = 'ioslides_presentation'
    reveal_js_presentation = 'revealjs::revealjs_presentation'
    slidy_presentation = 'slidy_presentation'
    beamer_presentation = 'beamer_presentation'
    # Dashboards.
    flex_dashboard = 'flexdashboard::flex_dashboard'
    # Tufte.
    tufte_handout = 'tufte::tufte_handout'
    tufte_html = 'tufte::tufte_html'
    tufte_book = 'tufte::tufte_book'
    # Other.
    html_vignette = 'html_vignette'
    github_markdown_document = 'github_document'


def update_render_options(initial_options, new_options):
    opts = initial_options.copy()
    if new_options is not None:
        for opt_str, v in new_options.items():
            try:
                opt = RenderOption(opt_str)
            except ValueError:
                pass
            else:
                opts[opt] = v
    return opts


def recover_chunk_source(code):
    return f'\n```python\n{code}```'


def recover_inline_source(code):
    return f'`\n{code}`'


def render_inline(code, outs, raise_errors):
    for content in outs.pop('error', []):
        sexc = execute.recover_exception(content)
        raise ValueError(f"Got exception: '{sexc}'")

    s = ''
    for content in outs.pop('text', []):
        s += content
    return s


def add_chunk_code(sects, s, options):
    show_code = (options[ChunkOption.show_code]
                 and options[ChunkOption.show_code_and_results])
    if show_code:
        sects.append(recover_chunk_source(s))


def add_result(sects, r, options, raw):
    show_results = (
        options[ChunkOption.show_code_and_results]
        and options[ChunkOption.results_style] != ResultsStyle.hide
    )
    if show_results:
        if options[ChunkOption.results_style] == ResultsStyle.as_is:
            v = raw
        else:
            v = r
        sects.append(v)


def render_chunk(code, options, outs, raise_errors):
    sects = []
    add_chunk_code(sects, code, options)

    for content in outs.pop('display_text', []):
        # Ugly way to avoid printing standard 'Figure <>' return.
        pass

    for content in outs.pop('text', []):
        lines = content.strip().split('\n')
        lines_prompt = [
            f'{options[ChunkOption.result_prefix]} {ln}'
            for ln in lines
        ]
        out = '\n'.join(lines_prompt)
        add_result(sects, out, options, raw=content)

    for content in outs.pop('html', []):
        # TODO: Identify tables, to allow captions.
        logger.info(f'Adding HTML: "{utils.trunc(content)}"')
        add_result(sects, content, options, raw=content)

    for content in outs.pop('image', []):
        logger.info(f'Adding image')
        el = figure_tmpl.render(
            fmt=content['format'],
            data=content['data'],
            slug=content['slug'],
            caption=content['caption'],
        )
        add_result(sects, el, options, raw=content)

    for content in outs.pop('script', []):
        logger.info(f'Adding script: "{utils.trunc(content)}"')
        el = script_tmpl.render(
            content=content,
        )
        add_result(sects, el, options, raw=content)

    for content in outs.pop('stdout', []):
        import pdb; pdb.set_trace()
        if options[ChunkOption.show_messages]:
            s = f'{options[ChunkOption.result_prefix]} "{content}"'
            add_result(sects, s, options, raw=content)

    for content in outs.pop('stderr', []):
        if options[ChunkOption.show_warnings]:
            s = f'WARNING {options[ChunkOption.result_prefix]} "{content}"'
            add_result(sects, s, options, raw=content)

    for content in outs.pop('error', []):
        sexc = execute.recover_exception(content)
        if raise_errors:
            raise ValueError(f"Got exception: '{sexc}'")
        else:
            s = f'ERROR {options[ChunkOption.result_prefix]} "{sexc}"'
            add_result(sects, s, options, raw=content)

    for kind in outs:
        for content in outs[kind]:
            raise NotImplementedError(f"{kind}: {content}")

    s = '\n\n'.join(sects) + '\n\n'
    return s


def _process_part(part, client, global_options):
    if isinstance(part, parse.InlineCode):
        logger.info(f'Processing inline code: "{utils.trunc(part.code)}"...')
        options = global_options.copy()
        if options[ChunkOption.run_code]:
            outs = execute.exec_code(
                client,
                part.code,
                implicit_display=True,
            )
            return render_inline(
                part.code,
                outs,
                raise_errors=not options[ChunkOption.show_errors],
            )
        else:
            return recover_inline_source(part.code)
        logger.info('Processed inline code.')
    elif isinstance(part, parse.CodeChunk):
        logger.info(f'Processing code chunk: "{utils.trunc(part.code)}"...')
        options = update_chunk_options(global_options, part.options)
        if options[ChunkOption.run_code]:
            outs = execute.exec_code(
                client,
                part.code,
                implicit_display=False,
            )
            return render_chunk(
                part.code,
                options,
                outs,
                raise_errors=not options[ChunkOption.show_errors],
            )
        else:
            return recover_chunk_source(part.code)
    elif isinstance(part, str):
        return part
    else:
        raise Exception


def process_parts(parts, header, global_options,
                  connection_file=None):
    client = execute.get_kernel_client(connection_file=connection_file)

    execute.exec_code(client, 'from nestler.preamble import *',
                      implicit_display=False)

    parts_evaled = []
    for part in parts:
        r = _process_part(part, client, global_options)
        parts_evaled.append(r)

    client.shutdown()
    s = ''.join(parts_evaled)
    return s, header


def get_pandoc_var_args(k, v):
    return ['--variable', f'{k}={v}']


def output_html_document(header, parts, output_fmt_str, global_options,
                         out_path_base,
                         connection_file=None):
    render_options = update_render_options(DEFAULT_RENDER_OPTS,
                                           header['output'][output_fmt_str])

    logger.info('Processing parsed document...')
    md_out_str, header = process_parts(parts, header, global_options,
                                       connection_file=connection_file)
    logger.info('Processing parsed document.')

    logger.info('Building pandoc arguments...')

    # Build up Pandoc's extra arguments.
    extra_pandoc_args = DEFAULT_EXTRA_PANDOC_ARGS[:]
    # Add custom CSS file.
    css_path = render_options.get(RenderOption.css_path)
    if css_path is not None:
        logger.info(f'Using CSS file "{css_path}"')
        extra_pandoc_args.extend(['--css', css_path])
    # Add any explicit extra arguments given in the header.
    doc_pandoc_args = render_options.get(RenderOption.pandoc_args)
    if doc_pandoc_args is not None:
        logger.info(f'Passing extra options to Pandoc: "{doc_pandoc_args}"')
        extra_pandoc_args.extend(doc_pandoc_args)
    # Add markdown extensions specified in the header to the defaults.
    pandoc_md_extensions = DEFAULT_PANDOC_MD_EXTENSIONS
    extra_md_extensions = render_options.get(RenderOption.markdown_extensions)
    if extra_md_extensions:
        ext_str = '\n'.join([f'    - {e}' for e in extra_md_extensions])
        logger.info(f'Enabling markdown extensions:\n{ext_str}')
        pandoc_md_extensions.extend([f'+{e}' for e in extra_md_extensions])
    # Handle self-contained header option.
    if render_options.get(RenderOption.make_self_contained):
        logger.info('Enabling "self-contained" option')
        extra_pandoc_args.append('--self-contained')
    # Handle format_smartly header option.
    if (render_options.get(RenderOption.format_smartly)
            and '+smart' not in pandoc_md_extensions):
        logger.info('Enabling "smart" markdown extension')
        pandoc_md_extensions.append('+smart')
    # Handle template header option.
    template_path = render_options.get(RenderOption.pandoc_template_path)
    if template_path is not None:
        logger.info(f'Using template "{template_path}"')
        extra_pandoc_args.extend(['--template', template_path])
    # Handle slides theme.
    slide_theme = render_options.get(RenderOption.slide_theme)
    if slide_theme is not None:
        logger.info(f'Setting slide theme to "{slide_theme}"')
        extra_pandoc_args.extend(get_pandoc_var_args('theme', slide_theme))
    # Handle slides color theme.
    slide_color_theme = render_options.get(RenderOption.slide_color_theme)
    if slide_color_theme is not None:
        logger.info(f'Setting slide color theme to "{slide_color_theme}"')
        extra_pandoc_args.extend(get_pandoc_var_args('colortheme', slide_theme))
    # Handle table of contents.
    if render_options.get(RenderOption.table_of_contents):
        logger.info('Enabling "table of contents" option')
        extra_pandoc_args.append('--table-of-contents')
    # Handle the table of contents depth.
    toc_depth = render_options.get(RenderOption.table_of_contents_depth)
    if toc_depth is not None:
        logger.info(f'Setting table of contents depth to "{toc_depth}"')
        extra_pandoc_args.extend(['--toc-depth', toc_depth])
    # Handle section numbers.
    if render_options.get(RenderOption.number_sections):
        logger.info('Enabling "number sections" option')
        extra_pandoc_args.append('--number-sections')
    # Handle LaTeX engine.
    latex_engine = render_options.get(RenderOption.latex_engine)
    if latex_engine is not None:
        logger.info(f'Setting LaTeX/PDF engine to "{latex_engine}"')
        extra_pandoc_args.extend(['--pdf-engine', latex_engine])
    # Handle LaTeX engine.
    highlight_style = render_options.get(RenderOption.syntax_highlight_style)
    if highlight_style is not None:
        logger.info(f'Setting syntax highlight style to "{highlight_style}"')
        extra_pandoc_args.extend(['--highlight-style', highlight_style])
    # Handle includes.
    includes = render_options.get(RenderOption.include_files)
    if includes is not None:
        in_header = includes.get('in_header')
        if in_header is not None:
            logger.info(f'Adding file in header "{in_header}"')
            extra_pandoc_args.extend(['--include-in-header', in_header])
        before_body = includes.get('before_body')
        if before_body is not None:
            logger.info(f'Adding file before body "{before_body}"')
            extra_pandoc_args.extend(['--include-before-body', before_body])
        after_body = includes.get('after_body')
        if after_body is not None:
            logger.info(f'Adding file after body "{after_body}"')
            extra_pandoc_args.extend(['--include-after-body', after_body])

    pandoc_header = header.copy()
    pandoc_header.pop('output')
    pandoc_metadata = yaml.dump(
        pandoc_header,
        default_flow_style=False,
        indent=4
    )
    md_out_str = f'---\n{pandoc_metadata}\n---\n{md_out_str}'

    if render_options.get(RenderOption.keep_markdown):
        md_out_path = 'intermediate.md'
        # if os.path.exists(md_out_path):
            # raise IOError(f'Target path for intermediate markdown file, "{md_out_path}", already exists')
            # pass
        # else:
        with open(md_out_path, 'w') as md_out_file:
            md_out_file.write(md_out_str)

    # in_fmt = 'markdown_strict' + ''.join(pandoc_md_extensions)
    in_fmt = 'markdown' + ''.join(pandoc_md_extensions)
    out_fmt = 'html'
    logger.info('Built pandoc arguments.')

    out_path = f"{out_path_base}{os.extsep}html"

    logger.info('Converting markdown output to HTML...')
    pypandoc.convert_text(
        source=md_out_str,
        to=out_fmt,
        format=in_fmt,
        extra_args=extra_pandoc_args,
        outputfile=out_path,
    )
    logger.info('Converted markdown output to HTML.')


FORMAT_TO_ROUTINE = {
    OutputFormat.html_document: output_html_document,
}
