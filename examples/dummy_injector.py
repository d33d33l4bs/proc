
'''This script allows to inject/unload a shared library into a process.'''


import argparse

from deedee.proc         import Process
from deedee.proc.plugins import getsym, call, syscall, loadlib, unloadlib


def load_library(args):
    victim = Process(args.pid, [
        getsym.by_lib_loading(),
        call.call_int3(),
        syscall.syscall(),
        loadlib.libc_dlopen()
    ])
    victim.attach()
    try:
        handler = victim.load_library(args.libc, args.lib)
    except Exception as e:
        print(f'An error occured during the injection: {e}.')
    else:
        print(f'Library sucessfully loaded (handler: {hex(handler)}).')
    victim.detach()

def unload_library(args):
    victim = Process(args.pid, [
        getsym.by_lib_loading(),
        call.call_int3(),
        unloadlib.libc_dlclose()
    ])
    victim.attach()
    try:
        victim.unload_library(args.libc, args.handler)
    except Exception as e:
        print(f'An error occured during the unloading: {e}.')
    else:
        print(f'Library sucessfully unloaded.')
    victim.detach()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dummy Shared Library Injector')
    parser.add_argument('pid', type=int, help='the pid in which the lib must be injected')

    subparsers = parser.add_subparsers(title='action')

    load = subparsers.add_parser('load', help='load a library')
    load.add_argument('libc', type=str, help='the path of the libc')
    load.add_argument('lib',  type=str, help='the path of the lib to inject')
    load.set_defaults(func=load_library)

    unload = subparsers.add_parser('unload', help='unload a library')
    unload.add_argument('libc',    type=str,                  help='path of the libc')
    unload.add_argument('handler', type=lambda s: int(s, 16), help='handler of the lib to unload (hexadecimal notation)')
    unload.set_defaults(func=unload_library)

    args = parser.parse_args()
    args.func(args)

