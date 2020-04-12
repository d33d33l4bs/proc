
from .plugin    import Plugin
from ..syscalls import SYS_mmap, SYS_munmap


class libc_dlclose(Plugin):

    name = 'unload_library'

    def run(self, process, libc_path, handler):
        dlclose_addr = process.get_sym(libc_path, '__libc_dlclose')
        ret          = process.call(dlclose_addr, handler)
        if ret != 0:
            raise RuntimeError('dlclose didn\'t return 0 (is your hanlder valid?)')

