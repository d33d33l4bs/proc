
'''Defines some strategies to read into the memory of a process.'''

from .plugin import Plugin


class proc_mem_read(Plugin):
    '''Allow to read the memory of a process by reading its /proc/mem file.

    Warnings
    --------
    It can only be used to read readable mappings!
    '''

    name = 'read_mem'

    def run(self, process, offset, size):
        with open(f'/proc/{process.pid}/mem', 'rb') as f:
            f.seek(offset)
            data = f.read(size)
        return data

