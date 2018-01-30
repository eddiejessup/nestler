from IPython.display import publish_display_data, display

PREAMBLE_VARS = {}

# Captions and references.

_DEFAULT_FIGURE_NOUN = 'figure'
_DEFAULT_TABLE_NOUN = 'table'
_DEFAULT_MPL_BACKEND = 'module://nestler.backend_inline'

PREAMBLE_VARS['registered_figures'] = []
PREAMBLE_VARS['registered_tables'] = []


# Figures.

def _publish_fig_caption(slug, txt):
    fig_nr = _slug_to_figure_nr(slug)
    publish_display_data({
        'application/json': {
            'kind': 'caption',
            'slug': slug,
            'fig_nr': fig_nr,
            'caption': txt,
        }
    })
    return fig_nr


def _slug_to_figure_nr(slug):
    return PREAMBLE_VARS['registered_figures'].index(slug) + 1


def _obj_ref(noun, up, counter):
    # TODO: Allow formatting counters like roman numerals and such.
    if up:
        noun = noun[0].upper() + noun[1:]
    s = f'{noun} {counter}'
    return s


def fig_ref(slug, noun=_DEFAULT_FIGURE_NOUN, up=False):
    return _obj_ref(noun, up, _slug_to_figure_nr(slug))


def Fig_ref(slug, noun=_DEFAULT_FIGURE_NOUN):
    return fig_ref(slug, noun=noun, up=True)


def register_fig(slug, caption=None, up=True, noun=_DEFAULT_FIGURE_NOUN):
    PREAMBLE_VARS['registered_figures'].append(slug)
    caption_txt = fig_ref(slug, noun=noun, up=up)
    if caption is not None:
        caption_txt += f': {caption}'
    counter = _publish_fig_caption(slug, caption_txt)
    return caption_txt, counter


def display_fig(fig, slug, caption):
    register_fig(slug, caption=caption)
    return display(fig)


# Tables.

def _slug_to_table_nr(slug):
    return PREAMBLE_VARS['registered_tables'].index(slug) + 1


def tbl_ref(slug, noun=_DEFAULT_TABLE_NOUN, up=False):
    return _obj_ref(noun, up, _slug_to_table_nr(slug))


def Tbl_ref(slug, noun=_DEFAULT_TABLE_NOUN):
    return tbl_ref(slug, noun=noun, up=True)


def register_table(slug):
    PREAMBLE_VARS['registered_tables'].append(slug)


def display_table(df, slug, caption=None, up=True):
    register_table(slug)

    ref = tbl_ref(slug, up=up)
    caption_txt = ref
    if caption is not None:
        caption_txt += f': {caption}'

    return display(
        df
        .style
        .set_caption(caption_txt)
        .set_table_styles([
            {'selector': 'caption', 'props': [('caption-side', 'bottom')]},
        ])
        .set_table_attributes('class="table"')
    )

try:
    import matplotlib
except ImportError:
    pass
else:
    matplotlib.use(_DEFAULT_MPL_BACKEND)


# Images

def insert_img(img, slug, caption, noun=_DEFAULT_FIGURE_NOUN):
    caption_txt, _ = register_fig(slug, caption)
    print(f'\n![{caption_txt}]({img} "{caption_txt}")')
