
'''Defines some strategies to load a library into another process.'''

from .plugin    import Plugin
from ..syscalls import SYS_mmap, SYS_munmap


# mmap prot constants
PROT_READ  = 1
PROT_WRITE = 2

# mmap flags constants
MAP_PRIVATE   = 0x02
MAP_ANONYMOUS = 0x20

# dlopen flags constants
RTLD_NOW = 0x02


class LibcDlopen(Plugin):

    def __init__(self, syscall, call, getsym):
        self._syscall = syscall
        self._call    = call
        self._getsym  = getsym

    def __call__(self, process, libc_path, lib_path):
        # allocate a new mapping
        prot    = PROT_WRITE | PROT_READ
        flags   = MAP_ANONYMOUS | MAP_PRIVATE
        mapping = self._syscall(process, SYS_mmap, 0, 8192, prot, flags, 0, 0)
        if mapping == 0:
            raise RuntimeError('mmap failed')
        print('mapping:', hex(mapping))
        # write the path lib into the beginning of the mapping
        path = lib_path.encode() + b'\x00'
        process.write_mem_array(mapping, path)
        # call dlopen
        dlopen_addr = self._getsym(process, libc_path, '__libc_dlopen_mode')
        print('dlopen addr:', hex(dlopen_addr))
        handler     = self._call(
            process,
            dlopen_addr,
            mapping,
            RTLD_NOW,
            stack_frame_addr=mapping+4096
        )
        print('handler:', hex(handler))
        # deallocate the mapping
        self._syscall(process, SYS_munmap, mapping, 8192)
        # return the handler
        if handler == 0:
            raise RuntimeError('dlopen returned NULL (is the path of your lib valid?)')
        return handler


class LibdlDlopen(Plugin):

    def __call__(self, process, libdl_path, lib_path):
        raise NotImplemented('this method is not implemented')


