# Startup and initialization

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

Reviewed early code shares state words and a local overlay handoff. The reset
entry and the ordered initialization chain remain unresolved.

- [Shared state access](#state-access)
- [Local overlay handoff and bounded search](#overlay-handoff)

<a id="state-access"></a>
## Shared state access

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| State write | `0x402c02fb` | 0 | `0x0000031b` | 6 |
| State read | `0x402c0339` | 0 | `0x00000359` | 6 |

- `0x402c02fb` writes register `d0` to runtime address `0x60504b24`
  (`block 0`, offset `0x0000031b`, length 6).
- `0x402c0339` reads the same runtime address into `d1`
  (`block 0`, offset `0x00000359`, length 6).
- Direct calls at `0x402c0334` and `0x402c0359` target `0x402c093c`.

The canonical instruction at that target is `mov d1,d3`, backed by block 0,
offset `0x0000095c`, length 1.

This establishes a shared runtime-state access and two direct control-flow
edges. It does not yet establish the reset entry, the state’s meaning, object
ownership, or initialization order.

A separate startup control word at `0x600011d0` has a bounded setter at
`0x402c0707`, followed by a far return. The startup-adjacent sequence at
`0x402c02b6..0x402c02bc` supplies `-1` and calls that setter; the same word is
read by the branch at the front of the delegated service below `0x402c15d1`.
This establishes one static write/read relationship, not the word's complete
lifecycle or runtime meaning.

**Next evidence:** [Connect the startup chain to
reset](../RESEARCH.md#r-startup).

<a id="overlay-handoff"></a>
## Local overlay handoff and bounded search

An exhaustive block-0 census found no full-width literal or supported direct
PC-relative edge naming initializer `0x402c0262`. The nearby early sequence
has an authenticated local-overlay handoff: at block-0 offset `0x000000c9` /
runtime `0x6e6000a9` it loads `0x6e6016a2` and jumps indirectly. That target is
backed by block-0 offset `0x000016c2` and begins by clearing `d2`. This closes
the local target mapping, but it still does not connect the handoff to reset or
to initializer `0x402c0262`. The bounded negative does not exclude another
block, ROM, runtime-built state, or a different block-0 address relation.

**Next evidence:** [Connect the startup chain to
reset](../RESEARCH.md#r-startup).
