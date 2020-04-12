
'''Defines some strategies to make the process call one of its functions.'''

from .plugin import Plugin


class call_int3(Plugin):

    name = 'call'

    CALL_ABI = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
    CALL_INT = b'\xff\xd0\xcc\x00\x00\x00\x00\x00'

    def run(self, process, fct_addr, *args, stack_frame_addr=None):
        '''Makes the process call one of its functions.

        Parameters
        ----------
        fct_addr : int
            The address of the function to call.
        *args
            Arguments of the function to call.
        stack_frame_addr : int, optional
            Set stack frame to this address.
        '''
        with process.get_regs_and_restore() as regs:
            # prepare and set all the registers
            regs.rax = fct_addr
            for i, arg in enumerate(args):
                setattr(regs, self.CALL_ABI[i], arg)
            if stack_frame_addr is not None:
                regs.rsp = stack_frame_addr
                regs.rbp = regs.rsp
            process.set_regs(regs)
            # call the fct
            with process.write_mem_words_and_restore(regs.rip, self.CALL_INT):
                process.continue_()
                # get the result
                process.get_regs(regs)
                ret = regs.rax
        return ret

