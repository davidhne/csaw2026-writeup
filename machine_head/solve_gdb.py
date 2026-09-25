import gdb
import string

gdb.execute("set startup-with-shell off")
gdb.execute("set confirm off")
gdb.execute("set pagination off")

CANDIDATES = string.ascii_letters + string.digits + "_{}!?-"
LEN = 53

gdb.execute("starti", to_string=True)
mappings = gdb.execute("info proc mappings", to_string=True)
base = None
for line in mappings.splitlines():
    if "masterkey" in line:
        base = int(line.split()[0], 16)
        break
gdb.execute("kill", to_string=True)

bp_addr = base + 0x1171
bp = gdb.Breakpoint(f"*{hex(bp_addr)}")
bp.enabled = True

flag = ""

for pos in range(LEN):
    found = None
    for ch in CANDIDATES:
        guess = flag + ch + "A" * (LEN - len(flag) - 1)
        bp.ignore_count = pos  # skip the earlier hits
        gdb.execute(f"run {guess}", to_string=True)
        r8d = int(gdb.parse_and_eval("$r8d"))
        gdb.execute("kill", to_string=True)
        if r8d == 1:
            found = ch
            break
    if found is None:
        print(f"ingen match ved posisjon {pos}")
        break
    flag += found
    print(pos, repr(flag))

print("FLAG:", flag)
