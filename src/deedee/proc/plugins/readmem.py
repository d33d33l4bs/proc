
'''Defines some strategies to read into the memory of a process.'''

from .plugin import Plugin


class ProcMemRead(Plugin):
    '''Allows to read the memory of a process by reading its /proc/mem file.

    Warnings
    --------
    It can only be used to read readable mappings.
    '''

    def __init__(self, auto_refresh=False):
        self._auto_refresh = auto_refresh
        self._f            = None

    def refresh(self, process):
        '''Close and open the proc mem file.'''
        if self._f is not None:
            self._f.close()
        self._f = open(f'/proc/{process.pid}/mem', 'rb')

    def __call__(self, process, offset, size):
        if self._f is None or self._auto_refresh:
            self.refresh(process)
        self._f.seek(offset)
        return self._f.read(size)

