
'''Retrieves a symbol adress into a process.'''


import argparse

import deedee.proc         as proc
import deedee.proc.plugins as plugins


def get_sym_addr(args):
    victim = proc.Process(args.pid)
    getsym = plugins.getsym.ByLibLoading()
    victim.attach()
    sym_adrr = getsym(victim, args.lib, args.sym)
    print(f'Address of {args.sym} ({args.lib}): {hex(sym_adrr)}.')
    victim.detach()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Symbol Address Getter')
    parser.add_argument('pid', type=int, help='process pid')
    parser.add_argument('lib', type=str, help='lib path')
    parser.add_argument('sym', type=str, help='sym name')
    args = parser.parse_args()
    get_sym_addr(args)

