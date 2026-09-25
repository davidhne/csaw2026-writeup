# machine_head

## Oppgaven

En stripped x86-64-binær (`masterkey`) som tar imot flagget som `argv[1]`. Den ekte
sjekkelogikken er ikke vanlig x86-kode, men et lite egendefinert bytecode-språk:
`main` inneholder en dispatch-loop som leser 3-byte instruksjoner
(`[opcode, operand1, operand2]`) fra et array i `.rodata` og tolker dem selv,
et hjemmelaget VM-oppsett, akkurat slik oppgavebeskrivelsen antydet ("speaks a
language you won't find in any disassembler's opcode table").


To uavhengige løsninger ligger i denne mappen, som begge fant samme flagg.

## `python-cracker.py` - statisk emulator

Leser en hex-dump av bytecode-arrayet (fra `DAT_00102040` i Ghidra, lagret som
`bytestring.txt`), reimplementerer opcode-semantikken i ren Python, og
brute-forcer ett tegn av gangen (32–126, printbart ASCII) mot target-verdien
for hver posisjon. Krever ingen kjørende instans av binæren.

```bash
python3 python-cracker.py
```

## `solve_gdb.py` - dynamisk brute-force via gdb

I stedet for å reimplementere VM-matematikken selv, bruker dette scriptet
gdb sitt Python-API til å la den ekte CPU-en gjøre utregningen: den setter et
breakpoint rett etter sammenlignings-instruksjonen i VM-loopen, kjører
binæren på nytt for hvert kandidat-tegn på hver posisjon, og leser av
suksess-registeret (`R8D`) for å avgjøre om tegnet var riktig. Bygger flagget
tegn for tegn på samme måte, men uten å måtte forstå eller reversere
opcode-aritmetikken i det hele tatt.

```bash
gdb -q --batch -x solve_gdb.py ./masterkey
```
(krever `masterkey`-binæren i samme mappe)


Reversing i Ghidra ga følgende opcode-tabell for VM-en:

| Opcode | Betydning |
|---|---|
| `0x7a` | `buf[op1] ^= op2` |
| `0x24` | `buf[op1] += op2` |
| `0xb2` | `buf[op1] = rol(buf[op1], op2)` |
| `0x1d` | `buf[op1] *= op2` (mod 256) |
| `0x4e` / `0x6d` | XOR / ADD mellom to buffer-slots |
| `0x91` | last inn tegn fra input-flagget |
| `0xa7` | sammenlign mot target-verdi, nullstill suksess-flagg ved mismatch |
| `0xe0` | sluttsjekk av suksess-flagget |

Bytecode-strømmen består av 53 kjedede blokker (én per tegn i flagget), der en
"carry"-tilstand bæres videre mellom tegnene (litt som CBC-kjeding) - så hvert
tegn avhenger av alle tegnene før det.



**Flag:** `csaw{cl1mb1ng_th3_v1rtu4l_st4ck_0n3_0pc0d3_4t_4_t1m3}`
