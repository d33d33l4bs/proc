
'''A collection of helper filters.

This module contains some predefined helpers allowing to filter the
get_maps output.

Examples
--------
Retrieving all the executable mapping of the libc:
>>> get_maps(1234, and_(has_perms('x'), has_path('/usr/lib64/libc-2.30.so'))

Warnings
--------
These filters seem to be a little overengineering things. The simple
lambda Python syntax may be more readable. Maybe I will remove them.
'''


def and_(*filters):
    '''Allows to make a "and" between several filters.'''
    def filter(mapping):
        for f in filters:
            if not f(mapping):
                return False
        return True
    return filter

def or_(*filters):
    '''Allows to make a "or" between several filters.'''
    def filter(mapping):
        for f in filters:
            if f(mapping):
                return True
        return False
    return filter

def has_path(path):
    '''Check the mapping path.'''
    def filter(mapping):
        return mapping.pathname == path
    return filter

def has_perms(*perms):
    '''Check the mapping permissions.'''
    def filter(mapping):
        return all(p in mapping.perms for p in perms)
    return filter

def has_size(eq=None, ge=None, le=None):
    '''Check the mapping size.'''
    def filter(mapping):
        if eq is not None:
            return mapping.size == eq
        valid = True
        if ge is not None:
            valid = valid and mapping.size >= ge
        if le is not None:
            valid = valid and mapping.size <= le
        return valid
    return filter

