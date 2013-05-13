'''Various utility funtionality--mostly for speed enhancements.'''

import collections
import functools

class memoized(object):
    '''Decorator to memoize a function.
    
    Caches the function's return value when it is called; returns the cached
    value (rather than reevaluating) if the function is called later with the 
    same arguments.
    
    @WARNING: This should be used for costly, time-consuming operations, NOT 
    operations that are "slow" because they have to build a large return value.
    Memoized functions are basically sanctioned memory leaks: memoizing 
    thousands of large lists or other objects may result in memory errors! For
    this reason, in any long-lived application, it is highly advised to clear
    the cache when its work is done!
    
    >>> @memoized
    >>> def test(x, y):
    >>>     # This is not a good function to memoize--large cached values!
    >>>     for i in range(x):
    >>>         dumb_list = range(y)
    >>>     return dumb_list
    >>> 
    >>> test(10000, 10000) # Slow
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ...9999]
    >>> test(10000, 10000) # Fast!
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ...9999]
    >>> test.cache.clear()
    >>> test(10000, 10000) # Slow again
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ...9999]
    
    This is based on a memoizing recipe from the Python Decorator Library:
    http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    '''

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.func = func
        self.cache = {}
    
    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            val = self.func(*args)
            self.cache[args] = val
            return val
    
    def __repr__(self):
        return self.func.__doc__
    
    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

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

def search(key, items):
    '''Quick & dirty binary search. Find `key` in `items`.

    Returns -1 if the key is not found.
    '''

    if not items:
        return -1
    if len(items) == 1:
        return 0 if items[0] == key else -1
    pivot = len(items)//2
    if key < items[pivot]:
        return search(key, items[:pivot])
    if key > items[pivot]:
        result = search(key, items[pivot:])
        return result + pivot if result >= 0 else result
    return pivot

def insensitive_string_search(key, items):
    '''Quick & dirty binary search. Find `key` in `items`.

    Returns -1 if the key is not found.

    @NOTE: This function is *not* case-sensitive!!
    '''

    if not items:
        return -1

    key = key.lower()

    if len(items) == 1:
        return 0 if items[0].lower() == key else -1
    pivot = len(items)//2

    pivot_string = items[pivot].lower()
    if key < pivot_string:
        return insensitive_string_search(key, items[:pivot])
    if key > pivot_string:
        result = insensitive_string_search(key, items[pivot:])
        return result + pivot if result >= 0 else result
    return pivot

def t():
    delimited_lines = {}
    non_delimited_lines = []
    with open('mhyph.txt', encoding='utf-8') as i:
        lines = i.readlines()
    with open('unhyph.txt', mode='w', encoding='utf-8') as o:
        for line_no, line in enumerate(lines):
            delimited_lines[line_no] = line.lower()
            non_delimited_lines.append((line.lower().replace('\u00a5',''), line_no))
        non_delimited_lines.sort()
        o.writelines([l for l, _ in non_delimited_lines])
    with open('newhyph.txt', mode='w', encoding='utf-8') as n:
        for _, line_no in non_delimited_lines:
            n.write(delimited_lines[line_no])
    
    

def main():
    # t()
    with open('unhyph.txt', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines()]
        print(insensitive_string_search('the', lines))

if __name__ == '__main__':
    main()