
import types
import functools
import ctypes
import os
import signal
import copy
import contextlib
import struct

from .plugins import Plugin
from .libc    import ptrace
from .libc    import uio
from .maps    import get_maps


##############
# Exceptions #
##############

class PtraceException(Exception):
    '''Raised when an error occured during a ptrace call.'''
    pass


class ProcessVMException(Exception):
    '''Raised when an error occured during a uio_[writev|readv] call.'''
    pass


###########
# Classes #
###########

class Process:
    '''Allows to manipulate a process: read/write its memory or registers.

    This class provides an higher abstraction than the ptrace module and can be
    extended by some plugins.
    '''

    def __init__(self, pid, plugins=[]):
        self._pid     = pid
        self._plugins = {}
        for plugin in plugins:
            self.add_plugin(plugin)

    @property
    def pid(self):
        return self._pid

    def add_plugin(self, plugin):
        self._plugins[plugin.name] = plugin
        setattr(self, plugin.name, functools.partial(plugin.run, self))

    def remove_plugin(self, plugin):
        delattr(self, plugin.name)
        del self._plugins[plugin.name]

    def is_plugin_loaded(self, plugin):
        return plugin.name in self._plugins

    def _call_ptrace(self, fct, *args):
        '''Helper method allowing to check if ptrace returned an error.

        Parameters
        ----------
        fct : fct
            One the ptrace helpers defined into the ptrace module (e.g attach).
        *args
            Arguments given to the ptrace helper. Do not provide the pid, this
            one is automatically given by this method.

        Raises
        ------
        PtraceException
            If a ptrace call failed.
        '''
        ctypes.set_errno(0)
        res   = fct(self._pid, *args)
        errno = ctypes.get_errno()
        if errno != 0:
            raise PtraceException(f'ptrace failed, errno: {errno}')
        return res

    def _wait(self, signal):
        '''Helper method allowing to wait for a specific signal.

        Parameters
        ----------
        signal : int
            The expected signal.

        Raises
        ------
        PtraceException
            If the received signal an the expected one are not equal.
        '''
        _, status = os.waitpid(self._pid, 0)
        if os.WIFSTOPPED(status):
            recv_sig = os.WSTOPSIG(status)
            if recv_sig != signal:
                return
                raise PtraceException(
                    f'tracee stopped by unexpected signal: ' \
                    f'{recv_sig} ({signal} expected)'
                )

    def get_maps(self, filter_=None):
        '''Returns the mappings of the process.

        Parameters
        ----------
        filter_
            A filter that will be given to maps.get_maps. It allows to filter
            mappings by using some properties (lib path, permissions, etc.).

        See Also
        --------
        maps.get_maps
        '''
        maps_ = get_maps(self._pid, filter_)
        return maps_

    def attach(self):
        '''Attaches the process with ptrace.'''
        self._call_ptrace(ptrace.attach)
        self._wait(signal.SIGSTOP)

    def detach(self):
        '''Detaches the process.'''
        self._call_ptrace(ptrace.detach)

    def step(self):
        '''Executes one instruction into the process, pauses it and returns.'''
        self._call_ptrace(ptrace.singlestep)
        self._wait(signal.SIGTRAP)

    def continue_(self):
        '''Continues the process execution while waiting for a signal.'''
        self._call_ptrace(ptrace.cont)
        self._wait(signal.SIGTRAP)

    def get_regs(self, regs=None):
        '''Gets all the process registers.

        Parameters
        ----------
        regs: ptrace.UserRegsStruct, optional
            If provided, this param will be filled with all the process
            registers. It allows to reuse an existing
            ptrace.UserRegsStruct instance.

        Returns
        -------
        ptrace.UserRegsStruct
            All the process registers.
        '''
        if regs is None:
            regs = ptrace.UserRegsStruct()
        self._call_ptrace(ptrace.getregs, regs)
        return regs

    def set_regs(self, regs):
        '''Sets all the process registers.

        Parameters
        ----------
        regs: ptrace.UserRegsStruct
            All the register of this structure will be set into the process.
        '''
        self._call_ptrace(ptrace.setregs, regs)

    @contextlib.contextmanager
    def get_regs_and_restore(self, regs=None):
        '''Contextmanager allowing to restore registers.

        Example
        -------
        >>> regs = p.get_regs()
        >>> print(regs.rax)
        0
        >>> with p.get_regs_and_restore() as regs:
        >>>     regs.rax = 5
        >>>     p.set_regs(regs)
        >>>     print(regs.rax)
        5
        >>> print(regs.rax)
        0
        '''
        if regs is None:
            regs = ptrace.UserRegsStruct()
        self.get_regs(regs)
        backup = copy.copy(regs)
        try:
            yield regs
        finally:
            self.set_regs(backup)

    def read_mem_words(self, addr, n=1):
        ''' Reads a word into the process memory.

        This one can be used to read from a mapping that has not the
        PROT_READ permission.

        Parameters
        ----------
        addr : int
            The address of the word to read.

        Returns
        -------
        bytes
            All the read bytes from the process memory. The result size
            is a multiple of the word size (8).
        '''
        result = bytearray()
        for off in range(n):
            word = self._call_ptrace(ptrace.peekdata, addr + 8 * off)
            result.extend(word.to_bytes(length=8, byteorder='little'))
        return result

    def write_mem_words(self, addr, data):
        '''Write a word into the process memory.

        This one can be used to write into a mapping that has not the
        PROT_WRITE permission.

        Parameters
        ----------
        addr : int
            The address where data will be written.
        data : bytes
            Data to write into the process memory. The data len must be a
            multiple of the word size (8).

        Raises
        ------
        ValueError
            If data is not a multiple of 8.
        '''
        if len(data) % 8 != 0:
            raise ValueError('len of data is not a multiple of 8')
        for off, word in enumerate(struct.iter_unpack('<Q', data)):
            self._call_ptrace(ptrace.pokedata, addr + 8 * off, word[0])

    @contextlib.contextmanager
    def write_mem_words_and_restore(self, addr, data):
        '''Contextmanager allowing to restore a written word.'''
        backup = self.read_mem_words(addr)
        try:
            self.write_mem_words(addr, data)
            yield
        finally:
            self.write_mem_words(addr, backup)

    def read_mem_array(self, addr, size):
        '''Reads a contiguous space of the process memory.

        Warnings
        --------
        This method uses `uio_readv`. Thus, it is not able to read from
        a mapping that has not the PROT_READ permission. You can do that by
        using `read_mem_words`.
        '''
        result     = ctypes.create_string_buffer(b'\x00' * size)
        local_iov  = uio.iovec(result, size)
        remote_iov = uio.iovec(addr, size)
        nb_read    = uio.read(self._pid, local_iov, remote_iov)
        if nb_read != size:
            raise ProcessVMException(
                f'invalid read number:' \
                f'{nb_read} ({size} expected)'
            )
        return result

    def write_mem_array(self, addr, data):
        '''Writes into a contiguous space of the process memory.

        Warnings
        --------
        This method uses `uio_writev`. Thus, it is not able to write
        from a mapping that has not the PROT_WRITE permission. You can do that
        by using `write_mem_words`.
        '''
        size       = len(data)
        local_iov  = uio.iovec(ctypes.c_char_p(data), size)
        remote_iov = uio.iovec(addr, size)
        nb_write   = uio.write(self._pid, local_iov, remote_iov)
        if nb_write != size:
            raise ProcessVMException(
                f'invalid write number:' \
                f'{nb_write} ({size} expected)'
            )

    @contextlib.contextmanager
    def write_mem_array_and_restore(self, addr, data):
        '''Contextmanager allowing to restore a written contiguous space.'''
        backup = self.read_mem_array(addr, len(data))
        try:
            self.write_mem_array(addr, data)
            yield
        finally:
            self.write_mem_array(addr, backup.raw)

