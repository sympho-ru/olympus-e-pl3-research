# Source anchors without an established subsystem owner

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

These bounded findings are useful reproduction anchors. The evidence does not
establish their proposed event identity or owning subsystem, so they are kept
separate from the capture and live-view descriptions.

- [Complete caller source span](#complete-caller)
- [Candidate receiver prologue](#receiver-prologue)

<a id="complete-caller"></a>
## Complete caller source span

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Complete caller | `unassigned` | 0 | `0x006b0204` | 56 |

The 56-byte block-0 range `[0x006b0204,0x006b023c)` extends the existing
48-byte same-start slice through the complete five-byte call at offset
`0x006b0232` and the return at `0x006b0239`. The shorter slice remains valid
range evidence, but its endpoint lies inside that call. This addition provides
a complete source span through the return. The finding has range-only support
and establishes no event identity, runtime execution, or image transfer.

**Next evidence:** [Establish the unassigned caller's
context](../RESEARCH.md#r-unassigned-caller).

<a id="receiver-prologue"></a>
## Candidate receiver prologue

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Register-save prologue | `0x6edc1104` | 0 | `0x007bfce4` | 5 |

The five-byte span at block-0 offset `0x007bfce4`, under local address view
`0x6edc1104`, has two reviewed instructions: `movm [d2,a2],(sp)` (length 2),
then `add -4,sp` at `0x6edc1106` (length 3). This establishes only the
register-save and stack-allocation prologue, ending before `0x6edc1109`. It
does not identify a receiver or dispatch table, prove an entry edge, or
establish register preservation through later indirect calls. No runtime
readiness, capture, image production, or transfer follows from this span.

**Next evidence:** [Continue the unassigned receiver
prologue](../RESEARCH.md#r-unassigned-receiver).
