
from .plugin import Plugin


class LibcDlclose(Plugin):

    def __init__(self, call, getsym):
        self._call   = call
        self._getsym = getsym

    def __call__(self, process, libc_path, handler):
        dlclose_addr = self._getsym(process, libc_path, '__libc_dlclose')
        ret          = self._call(process, dlclose_addr, handler)
        if ret != 0:
            raise RuntimeError('dlclose didn\'t return 0 (is your hanlder valid?)')

