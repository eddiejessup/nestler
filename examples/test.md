---
title: Better reporting the impact of changes
author: Elliot Marsden
date: "2017-12"
output:
    html_document:
        template: default.html
        theme: readable
        keep_md: true
---

```{python prepare, include=False}
import matplotlib.pyplot as plt

def figax(figsize=(12, 5), **fig_kwargs):
    fig = plt.figure(figsize=figsize, **fig_kwargs)
    ax = fig.gca()
    return fig, ax
```

```{python plot_bookings, echo=False}
fig, ax = figax()
ax.plot([1, 2], [3, 4])
display_fig(fig, slug='bookings', caption='Clobber')
```

`python Fig_ref('bookings')` should appear above.
