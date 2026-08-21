# Open firmware research

This page gives contributors starting points for extending the verified
Olympus E-PL3 Body 1.6 evidence. It is a research guide, not an additional
source of truth: the canonical data remains `evidence/ranges.jsonl` and
`evidence/instructions.jsonl`.

Research may overlap, and a well-supported negative result can still be
useful. Contributors submit authenticated ranges and instructions through the
workflow in [CONTRIBUTING.md](../CONTRIBUTING.md). A concise PR description may
explain the covered region and conclusion; it is review context rather than
canonical evidence or a semantic annotation.

## How to use the addresses on this page

Addresses such as `0x6f3307f5` are decoded runtime addresses written in
hexadecimal for readability. Instruction JSON stores the same value as a
decimal `address`. `block` and `offset` identify the authenticated bytes in a
decoded firmware block and are the values accepted by `source-range`.

| Area | Runtime address | JSON address | Block | Offset | Reviewed instruction |
|---|---:|---:|---:|---:|---|
| Boot writer | `0x402c02fb` | `1076626171` | 0 | `0x0000031b` | `mov d0,(0x60504b24)` |
| Boot reader | `0x402c0339` | `1076626233` | 0 | `0x00000359` | `mov (0x60504b24),d1` |
| Boot sink | `0x402c093c` | `1076627772` | 0 | `0x0000095c` | `mov d1,d3` |
| Still capture | `0x4096368d` | `1083586189` | 0 | `0x006a36ad` | `mov a0,a3` |
| Live-view root | `0x40ab9dbd` | `1084988861` | 0 | `0x007f9ddd` | `mov a0,a2` |
| Live-view callee | `0x40aba041` | `1084989505` | 0 | `0x007fa061` | `mov 1861203104,d0` |
| PTP path | `0x6f3307f5` | `1865615349` | 0 | `0x00d30815` | `movm [d2,d3,a2,a3],(sp)` |
| PTP record load | `0x6f3307fa` | `1865615354` | 0 | `0x00d3081a` | `mov -1602518580,a3` |
| PTP initializer | `0x6f330905` | `1865615621` | 0 | `0x00d30925` | `clr d0` |

## Good first contribution: extend instruction coverage

Choose a bounded function or control-flow corridor and continue from an
existing reviewed instruction boundary. Useful starting areas include:

- boot and startup around `0x402c02fb` and `0x402c093c`;
- still capture around `0x4096368d`;
- live-view construction around `0x40ab9dbd`;
- PTP handling around `0x6f3307f5`.

Stop at an explicit branch, return, indirect call, or already covered
boundary. Submit only authenticated source ranges and instruction rows.
Mention decoder disagreements in the PR rather than silently choosing one
interpretation.

## Map decoded offsets to runtime addresses

The relationship between container offsets, decoded blocks, declared load
addresses, copied regions, overlays, static pointers, and runtime addresses is
only partly understood.

A useful result establishes one reproducible mapping relationship or clearly
bounds one source of uncertainty. Submit the supporting ranges and
instructions, and explain the mapping in the PR.

## Recover the boot-entry and initialization chain

The authenticated instruction at `0x402c02fb` writes `d0` to runtime global
`0x60504b24`, and `0x402c0339` reads that global. Nearby authenticated direct
calls reach `0x402c093c`. The containing initializer entry, its caller,
connection to reset or boot entry, object ownership, lifetime, and ordered
subsystem startup remain unresolved.

A useful result connects an existing boundary to an authenticated predecessor,
successor, initialization owner, or task boundary without inferring execution
from a raw address coincidence.

The latest bounded block-0 census found no direct or full-width reference into
initializer `0x402c0262`. Continue only from a new caller-side mapping,
runtime-built table, another decoded block, or an authenticated ROM/RAM
observation; repeating whole-block literal or direct-edge scans is unlikely to
help.

## Continue the resolved still-corridor dispatch

The two calls at `0x40963771` and `0x409637d1` now resolve through the same
singleton table slot to runtime `0x6ebdb422` / source offset `0x005da002`.
For the caller-built argument, the recovered target selects tag `11780` and
reaches `0x4089a625`. The useful next boundary is the population and runtime
class of the list searched downstream, especially the object whose slot `+20`
is invoked. The tag path alone is not evidence of a shutter or image effect.

## Identify the live-view frame owner

The construction path beginning at `0x40ab9dbd` reaches `0x40aba041`, but no
frame-buffer owner, format, lifetime, or display/export consumer is established.
Previous exact string-address searches did not produce an instruction-aligned
owner reference, so another vocabulary or literal-address scan is unlikely to
help.

A useful result maps dispatch table `0x6eef8128` or `0x6eefb4a0`, or follows
the proven `outer+132` collection into one authenticated frame-producing or
frame-consuming relationship. The object binding and collection append are
already established; repeating the earlier vocabulary scan is not useful.

## Resolve a read-only PTP request and response lifecycle

PTP handling around `0x6f3307f5` and `0x6f330905` accesses runtime data record
`0xa07b81cc`, including its `+8` field at `0xa07b81d4`. These are runtime-memory
addresses, not decoded-block offsets. At code address `0x6f3307fa`, the same
32-bit record address is rendered as signed decimal `-1602518580` in the
reviewed instruction. Its 16-record queue producer/consumer, count, cleanup
drain, and one bounded dynamic copy path are established. The operation
ingress, valid-selector targets, absolute dynamic storage object, wire-level
completion, and runtime reachability remain unresolved.

A useful result now resolves one valid selector's indirect target, the
producer of that selector, or the absolute dynamic storage object reached by
the established 12-byte copy path. The queue owner, count semantics, cleanup
drain, and bounded dynamic copy are already established. Do not infer
operation names or wire completion from record layout alone.

## Resolve block 1's delegated materializer

The 69-record block-1 layout and its three block-0 materializer paths are now
established. One observation at delegated service `0x402e90bc`, with the
record-0 arguments, would distinguish copy/DMA from address mapping. Broad
rescans of block 1 are no longer the smallest useful step.

## Find block 2's consumer

The candidate `(0x00240000, 0x43d00400)` header and exact payload geometry are
authenticated, but no consumer proves their meaning. The next useful result is
one bounded static or emulated path that receives the decoded block and shows
whether those words are length/destination, source metadata, or something
else.

## Identify decoded block 4's external owner

Block 4 is now classified as a flat big-endian H8-family image, and an internal
420-byte source-to-runtime copy/call relationship is established. The open
question is external ownership: identify the exact chip/consumer and the path
that loads or starts the image. A raw string match in block 0 is not enough;
the useful result must bind a fifth-body descriptor or identifier to a read,
copy, write, or start operation.

## External evidence wanted: integrity and authentication

The official image can be decoded and reconstructed byte-identically. A
same-size nonempty body change can also be rescrambled and its additive tail
checksum repaired so the supplied host parser accepts the complete container.
That does not answer updater or device-side validation and authentication.

Useful evidence would be an independently inspectable verifier, an updater or
device validation path, technical documentation, or another reproducible
static artifact. Product pages, filenames, generic Olympus firmware behavior,
and requester-side access controls are not evidence of E-PL3 image
authentication.

## Maintaining this page

Open questions stay here until the maintainer accepts enough evidence to
answer or narrow them. Established relationships may then move into the small
reviewed [firmware map](FIRMWARE_MAP.md), while the canonical JSONL remains
firmware-only. Coordination and temporary ownership belong in GitHub issues or
PRs, not in this file.
