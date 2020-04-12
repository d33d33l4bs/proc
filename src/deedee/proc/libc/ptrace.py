
from ctypes import *
from ctypes import util


_all__ = [
    'UserRegsStruct', 'attach', 'detach', 'getregs', 'setregs',
    'peekdata', 'pokedata', 'singlestep', 'cont'
]


#############
# Constants #
#############

# __ptrace_request
PTRACE_PEEKTEXT   = 1
PTRACE_PEEKDATA   = 2
PTRACE_POKETEXT   = 4
PTRACE_POKEDATA   = 5
PTRACE_CONT       = 7
PTRACE_SINGLESTEP = 9
PTRACE_GETREGS    = 12
PTRACE_SETREGS    = 13
PTRACE_ATTACH     = 16
PTRACE_DETACH     = 17


###########
# Classes #
###########

class UserRegsStruct(Structure):
    _fields_ = [
        ('r15',      c_ulonglong),
        ('r14',      c_ulonglong),
        ('r13',      c_ulonglong),
        ('r12',      c_ulonglong),
        ('rbp',      c_ulonglong),
        ('rbx',      c_ulonglong),
        ('r11',      c_ulonglong),
        ('r10',      c_ulonglong),
        ('r9',       c_ulonglong),
        ('r8',       c_ulonglong),
        ('rax',      c_ulonglong),
        ('rcx',      c_ulonglong),
        ('rdx',      c_ulonglong),
        ('rsi',      c_ulonglong),
        ('rdi',      c_ulonglong),
        ('orig_rax', c_ulonglong),
        ('rip',      c_ulonglong),
        ('cs',       c_ulonglong),
        ('eflags',   c_ulonglong),
        ('rsp',      c_ulonglong),
        ('ss',       c_ulonglong),
        ('fs_base',  c_ulonglong),
        ('gs_base',  c_ulonglong),
        ('ds',       c_ulonglong),
        ('es',       c_ulonglong),
        ('fs',       c_ulonglong),
        ('gs',       c_ulonglong)
    ]


##########
# Ctypes #
##########

path = util.find_library('c')
libc = CDLL(path)
libc.ptrace.restype  = c_uint64
libc.ptrace.argtypes = [
    c_uint64,
    c_uint64,
    c_void_p,
    c_void_p
]


###########
# Helpers #
###########

def attach(pid):
    return libc.ptrace(PTRACE_ATTACH, pid, None, None)

def detach(pid):
    return libc.ptrace(PTRACE_DETACH, pid, None, None)
    
def getregs(pid, regs):
    return libc.ptrace(PTRACE_GETREGS, pid, None, byref(regs))

def setregs(pid, regs):
    return libc.ptrace(PTRACE_SETREGS, pid, None, byref(regs))

def peekdata(pid, addr):
    addr = c_void_p(addr)
    return libc.ptrace(PTRACE_PEEKDATA, pid, addr, None)

def pokedata(pid, addr, value):
    addr = c_void_p(addr)
    return libc.ptrace(PTRACE_POKEDATA, pid, addr, value)

def singlestep(pid):
    return libc.ptrace(PTRACE_SINGLESTEP, pid, None, None)

def cont(pid):
    return libc.ptrace(PTRACE_CONT, pid, None, None)

