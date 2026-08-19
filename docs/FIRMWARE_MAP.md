# Olympus E-PL3 firmware map

This page is the smallest reviewed map currently supported by the canonical
evidence. It gives firmware researchers useful entry points without making the
instruction JSONL carry semantic claims. The source of truth remains
[`evidence/ranges.jsonl`](../evidence/ranges.jsonl) and
[`evidence/instructions.jsonl`](../evidence/instructions.jsonl); every source
span listed here can be reauthenticated against a verified Body 1.6 image.

Labels such as “boot”, “live view”, and “PTP” describe the current research
area. They are not recovered Olympus symbol names. A decoded instruction proves
a static instruction boundary and operation, not that the path executes on a
particular device state.

## Current coverage

| Decoded block | Canonical public coverage |
|---:|---|
| 0 | 9,236 authenticated ranges and 39,415 reviewed MN103 instruction rows |
| 1 | No authenticated ranges or instructions yet |
| 2 | No authenticated ranges or instructions yet |
| 3 | 21 authenticated ranges; no reviewed instructions yet |
| 4 | 3,115 authenticated ranges covering the full 65,536-byte decoded block; no reviewed instructions yet |

This is partial, non-contiguous coverage rather than a complete disassembly.
Block offsets and runtime addresses are separate coordinates. Block 0 has more
than one observed runtime-address relationship, so do not derive a runtime
address by adding one global load base. Use an explicit authenticated
`(address, block, offset)` anchor from the instruction evidence.

## Established regions

### Startup-state access

- `0x402c02fb` writes register `d0` to runtime address `0x60504b24`
  (`block 0`, offset `0x0000031b`, length 6).
- `0x402c0339` reads the same runtime address into `d1`
  (`block 0`, offset `0x00000359`, length 6).
- Direct calls at `0x402c0334` and `0x402c0359` target `0x402c093c`.

This establishes a shared runtime-state access and two direct control-flow
edges. It does not yet establish the reset entry, the state’s meaning, object
ownership, or initialization order.

### Live-view research corridor

The reviewed corridor begins at `0x40ab9dbd` (`block 0`, offset
`0x007f9ddd`). A direct call at `0x40ab9e73` targets `0x40aba041`. The
authenticated containing span is:

```text
block=0 offset=0x007f9ddd length=382
sha256=592f4b119e2fa9efc4a4b68db11331e49a85530860a935faed3ba833eb965449
```

The accepted evidence does not yet identify a frame-buffer owner, pixel
format, lifetime, or display/export consumer.

## Established PTP-adjacent record initialization

This is the first bounded corridor with a useful direct data effect. Two
authenticated source spans cover the caller sequence and its helper:

```text
caller: block=0 offset=0x00d30925 length=41
        sha256=3211fdb645a1beb403b214d28add1330dc68ecda34742d4de18c669b2f38dfb5
helper: block=0 offset=0x0010cc15 length=15
        sha256=ebd2aaafb2640932096d3f028009e1c52d9e5a230ccfa93d75717fc991c32ef3
```

The reviewed instructions establish this static chain:

| Runtime address | Established instruction effect |
|---:|---|
| `0x6f330905` | Clear `d0`. |
| `0x6f33091e` | Load `a0` with `0xa07b81cc` (rendered as signed decimal `-1602518580` in the canonical decode). |
| `0x6f330924` | Load `d1` with 256. |
| `0x6f330927` | Directly call `0x6e70cbf5`. |
| `0x6e70cbf5` | Clear the counter `d2`; compare it with `d1`. |
| `0x6e70cbf9` | Copy the destination from `a0` to `a1`. |
| `0x6e70cbfb` | Store byte `d0` through `a1`. |
| `0x6e70cbfd` | Increment the counter and destination, compare, and loop conditionally. |
| `0x6e70cc01` | Return. |

Therefore, on this statically decoded path, the helper zero-fills 256 bytes
beginning at runtime address `0xa07b81cc`. This includes the `+8` address
`0xa07b81d4` referenced elsewhere in the PTP research corridor.

The current boundary is deliberately narrow. The evidence does **not** yet
establish:

- the record’s complete constructor, owner, lifetime, or later contents;
- an operation-code-to-handler mapping;
- request and response buffer ownership or completion status;
- runtime reachability of this path in a specific camera state.

Extending any one of those relationships is an open task in
[RESEARCH.md](RESEARCH.md). The commands needed to reproduce and extend these
windows are in [ANALYSIS.md](ANALYSIS.md).
