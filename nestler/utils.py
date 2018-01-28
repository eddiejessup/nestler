def trunc(s, lim=100):
    s = s.strip()
    if len(s) > lim:
        return s[:lim] + '...'
    else:
        return s
