
'''This script allows to inject/unload a shared library into a process.'''


import argparse

import deedee.proc         as proc
import deedee.proc.plugins as plugins


def load_library(args):
    victim  = proc.Process(args.pid)
    syscall = plugins.syscall.SyscallByInstrReplacement()
    call    = plugins.call.CallInt3()
    getsym  = plugins.getsym.ByLibLoading()
    loadlib = plugins.loadlib.LibcDlopen(syscall, call, getsym)
    victim.attach()
    try:
        handler = loadlib(victim, args.libc, args.lib)
    except Exception as e:
        print(f'An error occured during the injection: {e}.')
    else:
        print(f'Library sucessfully loaded (handler: {hex(handler)}).')
    victim.detach()

def unload_library(args):
    victim    = proc.Process(args.pid)
    call      = plugins.call.CallInt3()
    getsym    = plugins.getsym.ByLibLoading()
    unloadlib = plugins.unloadlib.LibcDlclose(call, getsym)
    victim.attach()
    try:
        unloadlib(victim, args.libc, args.handler)
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

