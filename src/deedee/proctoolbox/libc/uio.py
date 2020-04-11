
from ctypes import *
from ctypes import util


__all__ = ['IOVec', 'read', 'write', 'iovec']


###########
# Classes #
###########

class IOVec(Structure):
    _fields_ = [
        ('iov_base', c_void_p),
        ('iov_len',  c_size_t),
    ]


##########
# Ctypes #
##########

path = util.find_library('c')
libc = CDLL(path)

# process_vm_readv
libc.process_vm_readv.restype = c_ssize_t
libc.process_vm_readv.argtype = [
    c_uint64,
    POINTER(IOVec),
    c_ulong,
    POINTER(IOVec),
    c_ulong,
    c_ulong
]

# process_vm_writev
libc.process_vm_writev.restype = libc.process_vm_readv.restype
libc.process_vm_writev.argtype = libc.process_vm_readv.argtype


###########
# Helpers #
###########

def read(pid, local_iov, remote_iov):
    return libc.process_vm_readv(pid, byref(local_iov), 1, byref(remote_iov), 1, 0)

def write(pid, local_iov, remote_iov):
    return libc.process_vm_writev(pid, byref(local_iov), 1, byref(remote_iov), 1, 0)

def iovec(base, size):
    return IOVec(cast(base, c_void_p), size)

