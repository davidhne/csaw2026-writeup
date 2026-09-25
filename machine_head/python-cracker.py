data = open('bytestring.txt').readline()
b = bytes.fromhex(data.replace(' ', '').strip())
n = len(b) // 3
triplets = [(b[i*3], b[i*3+1], b[i*3+2]) for i in range(n)]


def rol8(x, r):
    r &= 7
    return ((x << r) | (x >> (8 - r))) & 0xff


# opcode -> hva instruksjonen gjør
# 0x7a XOR literal | 0x24 ADD literal | 0xb2 ROL literal | 0x1d MUL literal
# 0x4e XOR buf[op2] | 0x6d ADD buf[op2] | 0x91 last inn tegn fra flagget
# 0xa7 sammenlign mot target | 0xe0 slutt

buf1 = 0 ^ triplets[0][2]   # engangs-init av carry-tilstanden
flag = bytearray()
i = 1

while i < len(triplets):
    if triplets[i][0] == 0xe0:
        break

    block = triplets[i:i + 12]   # 12 instruksjoner per tegn
    carry = buf1
    found = None

    for ch in range(32, 127):
        val = ch
        val ^= block[1][2]                 # 0x7a XOR
        val = (val + block[2][2]) & 0xff    # 0x24 ADD
        val = rol8(val, block[3][2])        # 0xb2 ROL
        val ^= block[4][2]                  # 0x7a XOR
        val = (val * block[5][2]) & 0xff    # 0x1d MUL
        val ^= carry                        # 0x4e XOR med carry
        if val == block[7][2]:              # 0xa7 sammenlign mot target
            found = ch
            break

    if found is None:
        print("ingen match ved tegn", len(flag))
        break

    flag.append(found)
    buf1 = (carry + found) & 0xff   # 0x6d ADD
    buf1 = rol8(buf1, block[10][2])  # 0xb2 ROL
    buf1 ^= block[11][2]             # 0x7a XOR
    i += 12

print(flag.decode(errors="replace"))
