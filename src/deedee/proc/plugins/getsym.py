
'''Defines some strategies to get the address of a symbol.'''

import os
import ctypes

from .plugin import Plugin
from ..maps  import get_maps


class by_lib_loading(Plugin):
    '''Get a sym address by loading the library into the host process.

    Here is its internal working:

        1. Loads the lib in which the sym is defined thanks to `dlopen`.
        2. Gets the addr of the lib.
        3. Gets the sym addr into the lib.
        4. Computes the offset between the sym addr and the lib addr.
        5. Gets the addr of the lib into the target process.
        6. Computes the sym addr: step5 + step4.

    Warnings
    --------
    This strategy can be a heavy process and may result in unwanted effects.
    Indeed, it loads the library into the host process! If some constructors
    are defined into, these one will be executed by the host process.
    '''

    name = 'get_sym'

    def run(self, process, lib_path, sym_name):
        '''
        Parameters
        ----------
        lib_path : str
            The path to the library in which the function is defined.
        sym_name : str
            The name of the function whose address is retrieved.

        Returns
        -------
        int
            The function address.

        Raises
        ------
        RuntimeError
            No executable mapping is found into the library.
        '''
        # load the lib into the local process
        self_pid = os.getpid()
        lib      = ctypes.CDLL(lib_path)
        filter_  = lambda m: m.pathname == lib_path and 'w' in m.perms
        # get the lib mem base addr
        mappings = get_maps(self_pid, filter_)
        if len(mappings) == 0:
            raise RuntimeError('impossible to find an executable mapping into the lib')
        base_addr = mappings[0].start_address
        # get the sym addr of this process
        sym      = getattr(lib, sym_name)
        addr     = ctypes.addressof(sym)
        addr     = ctypes.cast(addr, ctypes.POINTER(ctypes.c_ulonglong))
        sym_addr = addr.contents.value
        # compute and return the offset
        sym_offset = sym_addr - base_addr
        # get the lib addr in the target process
        mappings = process.get_maps(filter_)
        if len(mappings) == 0:
            raise RuntimeError('impossible to find an executable mapping into the lib')
        lib_addr = mappings[0].start_address
        # compute the remote sym addr
        sym_addr = lib_addr + sym_offset
        return sym_addr


class by_elf_parsing(Plugin):

    def get_sym(self, process, lib_path, sym_name):
        '''Get a sym address by parsing the library in which the sym is defined.

        This strategy parses the output of the `readelf` command.
        Below is a summary of its working:

            1. Gets the sym offset into the lib.
            2. Gets the virtual address of the executable mapping of the lib.
            3. Gets the addr of the lib into the target process.
            4. Compute the address: offset + (step3 - step2)

        Warnings
        --------
        This strategy needs the command `readelf` to work.
        '''
        pass

