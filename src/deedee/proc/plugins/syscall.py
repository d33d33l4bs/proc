
'''Defines some strategies to make the process call a syscall.'''

from .plugin import Plugin


class SyscallByInstrReplacement(Plugin):
    '''Replaces the current instruction by a syscall.

    This basic plugin works in this way:

        1. Sets the syscall params into registers.
        2. Replaces the instruction pointed by rip by a syscall instruction.
        3. Made the process to singlestep.
        4. Restore all the registers and the original overriden instruction.

    '''

    SYSCALL_ABI = ['rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9']
    SYSCALL     = b'\x0f\x05\x00\x00\x00\x00\x00\x00'

    def __call__(self, process, syscall, *args):
        '''
        Parameters
        ----------
        syscall : int
            The syscall number to call.
            A list of all the syscall is provided into the `syscalls` module.
        *args
            Arguments of the syscall.
        '''
        with process.get_regs_and_restore() as regs:
            # prepare and set all the registers
            regs.rax = syscall
            for i, arg in enumerate(args):
                setattr(regs, self.SYSCALL_ABI[i], arg)
            process.set_regs(regs)
            # call the syscal
            with process.write_mem_words_and_restore(regs.rip, self.SYSCALL):
                process.step()
                # get the result
                process.get_regs(regs)
                ret = regs.rax
        return ret

