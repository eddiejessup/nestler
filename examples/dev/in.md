---
title: Pilloried duplicity
author: Elliot Marsden
date: "2017-12"
output:
    html_document:
        template: default.html
        theme: readable
        keep_md: true
---

# Test document for PyMarkdown

## Prelude: Markdown

Here is some easy stuff to get started: let's just check we don't get tripped up by ordinary markdown-style code markup. To show files at the terminal, one can run the program `ls`. The `-l` flag provides more information. Here is how a typical usage scenario might look:

```bash
❯ ls -l
total 56
-rw-r--r--  1 ejm  staff  1524  7 Nov 21:22 LICENSE
-rw-r--r--  1 ejm  staff     6  7 Nov 21:22 README.md
-rw-r--r--  1 ejm  staff    46  7 Nov 21:22 Setup.hs
drwxr-xr-x  5 ejm  staff   160  8 Nov 23:39 app
-rw-r--r--@ 1 ejm  staff  1297 10 Aug  1992 cmr10.tfm
-rw-r--r--  1 ejm  staff  1841  9 Nov 00:05 hex.cabal
drwxr-xr-x  5 ejm  staff   160  8 Nov 23:06 src
-rw-r--r--  1 ejm  staff  2194  9 Nov 00:03 stack.yaml
drwxr-xr-x  3 ejm  staff    96  7 Nov 21:22 test
-rw-r--r--  1 ejm  staff   160  8 Nov 20:19 test.tex
```

## Meat: Inline

Ok let's ramp it up: some stateless inline code. A typical realisation of the repeated application of successor function, to the natural numbers, represented through an infix operator, might look like the following: 2 + 2 = `python sum([2 for _ in range(2)])`.

Let's take that a step further: let's carry state between those inline chunks. That same operation again: 2 + 2 = `python a=sum([2 for _ in range(2)]);a`. One more time, using that result we just stored: 2 + 2 = `python a`.

## Throwing chunks

Smashing it. I think the next smallest step would be just to define the state in a chunk, rather than inline. So let's do that. I'm not expecting any output at this point.

```{python }
b = 2 - 2
```

Now let's call up that function. Who knows what result we got? I do. I expect this to make sense to you the reader: 2 - 2 = `python b`.

## Put yourself out there

Now let's enter the strange world of chunk output. First, some boring old standard-out stream output, so yucky nobody would want to see it.

```{python }
print(f"2 + 2 = {2 + 2}")
```

Another way we can get plaintext output is to write an expression that returns something, on the last line of a chunk. Let's try that.

```{python }
b = 2 + 2
b
```

## Providing optionality

I'm not sure this is the best direction to go, in terms of gradually increasing complexity, but here goes. There are a few options to control output, so let's try them.

`comment` lets us change the prompt that starts each plaintext output line.

```{python comment=":"}
b
```

Disabling `echo` lets us hide the code chunk, and only show the output.

```{python echo=False}
b
```

Disabling `eval` stops the code chunk from even being run.

```{python eval=False}
b
```

Disabling `include` runs the code, but hides both the code and its output.

```{python include=False}
c = 2 * 8
```

```{python}
print(f"In the last non-included chunk I computed 'c' to be {c}")
```

We can just hide the results by setting the `results` option to `"hide"`.

```{python results="hide"}
print(f"In the last non-included chunk I computed 'c' to be {c}")
```

While we're on the subject, another potentially easy one to implement is the option `"asis"`, which stops any post-processing of the results.

```{python results="asis"}
print(f"\n#### Let's inject some _emphatic_ _markdown_ into _proceedings_\n")
```

The last simple textual options I can see are about showing errors, warnings and messages. I'm going to interpret these as:

- Disabling `message` hides stream messages to standard out
- Disabling `warning` hides stream messages to standard error
- Enabling `error` shows exceptions in the output, and keeps running

So calls to `print` to standard out should produce nothing, if `message` is disabled:

```{python message=False}
import sys
print(f"Help, help, the computer is on fire!")
print(f"Help, help, the computer really is on fire!", file=sys.stderr)
```

If I disable `warning`, we should now see nothing from a `print` call to standard error:

```{python warning=False}
import sys
print(f"Help, help, the computer is on fire!")
print(f"Help, help, the computer really is on fire!", file=sys.stderr)
```

This warnings thing should also work if we use Python's warnings machinery. Let's take a look:

```{python}
import warnings
warnings.warn(f"Help, help, the computer really is on fire!")
```

Looks ok. Now for errors. Let's make one:

```{python error=True}
raise Exception("Oh gee the computer burned down.")
```
