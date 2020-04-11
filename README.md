# Introduction

Proctoolbox is a simple library I made to serve my own purposes.


# Warnings

You can use this one but remember that its primary goal is to store some pieces of code I wrote for my projects.
Therefore don't expect to see a beautiful code or a pretty architecture.


# Install

```bash
git clone https://github.com/d33d33l4bs/proctoolbox.git
cd proctoolbox
python setup.py install
```


# Examples

## Attach/Detach/Continue/Singlestep a process

```python
from deedee.proctoolbox.process import Process

process = Process(pid)

# attach
process.attach()

# execute one instruction
process.step()

# continue the process
process.continue_()

# detach
process.detach()
```

## Read the process registers

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.attach()
regs = process.get_regs()
```

## Write the process registers

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.attach()
regs = process.get_regs()
regs.rax = 1
regs.rdi = 2
process.set_regs(regs)
```

## Make an auto registers restore

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.attach()
with process.get_regs_and_restore() as regs:
    # all registers modification will be restored after the context manager exit
    regs.rax = 1
    regs.rdi = 2
    process.set_regs(regs)
    # do others things here like syscall/call
# here the registers are restored with their original values
```

## Get all the mappings of a process

Without a `Process` instance:

```python
from deedee.proctoolbox.maps import get_maps

get_maps(1234)
```

With a `Process` instance:

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.get_maps()
```

## Get all the writable mappings of a process with a size greater or equal to 4096

```python
from deedee.proctoolbox.maps import get_maps

get_maps(1234, lambda m: 'w' in m.perms and m.size >= 4096)
```

## Get a symbol address into another process memory (support ASLR)

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.attach()
printf_addr = process.get_sym_addr('/usr/lib64/libc-2.30.so', 'printf')
```

## Make a process call a function

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.attach()
exit_addr = process.get_sym_addr('/usr/lib64/libc-2.30.so', 'exit')
process.call(exit_addr, 0)
```

## Make a process call a syscall

```python
from deedee.proctoolbox.process import Process

NR_exit = 60

process = Process(pid)
process.attach()
process.syscall(NR_exit, 0)
```

## Allocate a new mapping into a process

```python
from deedee.proctoolbox.process import Process

NR_MMAP = 9

PROT_READ  = 1
PROT_WRITE = 2
PROT_EXEC  = 4

MAP_PRIVATE   = 0x02
MAP_ANONYMOUS = 0x20

SIZE = 1024

process = Process(pid)
process.attach()

prot    = PROT_WRITE | PROT_READ
flags   = MAP_ANONYMOUS | MAP_PRIVATE
mapping = target.syscall(NR_MMAP, 0, SIZE, prot, flags, 0, 0)
```

## Read data from the memory of a process

**Method #1:**

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.attach()

# read 5 words from 0x0011223344556677
words = process.read_mem_words(0x0011223344556677, n=5)
```

**Method #2:**

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.attach()

# read 5 bytes from 0x0011223344556677
words = process.read_mem_array(0x0011223344556677, n=5)
```

## Write into the memory of a process

**Method #1:**

```python
from deedee.proctoolbox.process import Process

PAYLOAD = b'\x0f\x05\x00\x00\x00\x00\x00\x00'

process = Process(pid)
process.attach()

# write a word into 0x0011223344556677
words = process.write_mem_words(0x0011223344556677, PAYLOAD)
```

This method uses `ptrace`. Therefore it can be used to write some words into a
non writable mapping.

**Method #2:**

```python
from deedee.proctoolbox.process import Process

process = Process(pid)
process.attach()

# write a string into 0x0011223344556677
words = process.write_mem_array(0x0011223344556677, b'Hello World!')
```

This method can only write on writable mapping.

## Write into a memory then restore a backup

A context manager allow to undo mem modifications:

```python
from deedee.proctoolbox.process import Process

PAYLOAD = b'\x0f\x05\x00\x00\x00\x00\x00\x00'

process = Process(pid)
process.attach()

with process.write_mem_words_and_restore(0x0011223344556677, PAYLOAD):
    # here the word is written into 0x0011223344556677
    # you can do some things with the process (continue it, etc.)
# here the write is undo
```

A similar context manager is written for `write_mem_array`: `write_mem_array_and_restore`.
