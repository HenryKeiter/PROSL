def split_string(s, *delimiters, split_whitespace=True):
    '''Split a string by any number of delimiters.

    If `split_whitespace` is given, the string will first be split by the 
    default str.split() (no arguments) method.

    Returns a list.
    '''

    if not delimiters:
        return s.split()
    delimiters = list(delimiters)
    splitlist = s.split() if split_whitespace else s.split(delimiters.pop())
    for d in delimiters:
        tmp = []
        for s in splitlist:
            tmp.extend(s.split(d))
        splitlist = tmp
    return splitlist

def search(a, x):
    '''Quick & dirty binary search. Find `x` in `a`.'''

    if not a:
        raise ValueError("Key not found.")
    midpt = len(a)//2
    if a[midpt] > x:
        return search(a[:midpt], x)
    elif a[midpt] < x:
        return midpt+1+search(a[midpt+1:], x)
    return midpt

