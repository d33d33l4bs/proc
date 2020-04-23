
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


class libc_dlopen(Plugin):

    name = 'load_library'

    def run(self, process, libc_path, lib_path):
        # allocate a new mapping
        prot    = PROT_WRITE | PROT_READ
        flags   = MAP_ANONYMOUS | MAP_PRIVATE
        mapping = process.syscall(SYS_mmap, 0, 8192, prot, flags, 0, 0)
        if mapping == 0:
            raise RuntimeError('mmap failed')
        # write the path lib into the beginning of the mapping
        path = lib_path.encode() + b'\x00'
        process.write_mem_array(mapping, path)
        # call dlopen
        dlopen_addr = process.get_sym(libc_path, '__libc_dlopen_mode')
        handler     = process.call(
            dlopen_addr,
            mapping,
            RTLD_NOW,
            stack_frame_addr=mapping+4096
        )
        # deallocate the mapping
        process.syscall(SYS_munmap, mapping, 8192)
        # return the handler
        if handler == 0:
            raise RuntimeError('dlopen returned NULL (is the path of your lib valid?)')
        return handler


class libdl_dlopen(Plugin):

    name = 'load_library'

    def run(self, process, libdl_path, lib_path):
        pass


