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
| Live-view teardown | `0x40ab9dbd` | `1084988861` | 0 | `0x007f9ddd` | `mov a0,a2` |
| Live-view callee | `0x40aba041` | `1084989505` | 0 | `0x007fa061` | `mov 1861203104,d0` |
| PTP path | `0x6f3307f5` | `1865615349` | 0 | `0x00d30815` | `movm [d2,d3,a2,a3],(sp)` |
| PTP record load | `0x6f3307fa` | `1865615354` | 0 | `0x00d3081a` | `mov -1602518580,a3` |
| PTP initializer | `0x6f330905` | `1865615621` | 0 | `0x00d30925` | `clr d0` |

## Good first contribution: extend instruction coverage

Choose a bounded function or control-flow corridor and continue from an
existing reviewed instruction boundary. Useful starting areas include:

- boot and startup around `0x402c02fb` and `0x402c093c`;
- still capture around `0x4096368d`;
- live-view teardown around `0x40ab9dbd` and wrapper `0x40aba091`;
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
initializer `0x402c0262`. The local-overlay handoff at block-0 offset `0xc9` /
runtime `0x6e6000a9` is now mapped through its indirect target
`0x6e6016a2`, backed by source offset `0x16c2`. The useful next result is the
authenticated predecessor or runtime-built pointer that supplies this handoff
and connects it to reset without treating the local overlay as a global load
base. Repeating whole-block literal or direct-edge scans is unlikely to help.

## Continue the resolved still-corridor dispatch

The two calls at `0x40963771` and `0x409637d1` now resolve through the same
singleton table slot to runtime `0x6ebdb422` / source offset `0x005da002`.
For the caller-built argument, the recovered target selects tag `11780` and
reaches `0x4089a625`; accepted coverage now continues through object
initialization, value association, and append into the searched list through
`0x4089a73b`. The useful next boundary is the list's runtime class and the
object whose slot `+20` is invoked. The population path is not evidence of a
shutter or image effect.

## Identify the live-view frame owner

The lazy singleton accessor at `0x40ab9cbd` constructs through `0x40ab9ceb`;
the corridor beginning at `0x40ab9dbd` is its reverse-order destructor, not
its constructor. Dispatch table `0x6eefb4a0` is mapped, with slot `+0x10`
resolving to wrapper `0x40aba091`; the 16-slot table `0x6eef8128` is now mapped
too, with slot `+0` conditionally resolving to `0x6edec9be`. No frame-buffer
owner, format, or display/export consumer is established. Previous exact
string-address scans did not produce an instruction-aligned owner reference,
so another vocabulary scan is unlikely to help.

A useful result identifies which independently decoded slot of `0x6eef8128`
or `0x6eefb4a0` carries the `outer+132` collection element into
`0x4052c090` or the `0x40aac8b4` append, then follows one authenticated edge
to a concrete frame handle. The lifecycle, object binding, collection append,
and the two mapped tables are already established.

## Resolve a read-only PTP request and response lifecycle

PTP handling around `0x6f3307f5` and `0x6f330905` accesses runtime data record
`0xa07b81cc`, including its `+8` field at `0xa07b81d4`. These are runtime-memory
addresses, not decoded-block offsets. At code address `0x6f3307fa`, the same
32-bit record address is rendered as signed decimal `-1602518580` in the
reviewed instruction. Its 16-record queue producer/consumer, count, cleanup
drain, two-entry `0x40000`-byte backing-buffer pool, one bounded dynamic copy
path, and one `0xbb02` reply lifecycle are established. Halfword
`0xa07b82d0` is co-reset but is absent from the reviewed append, shift, drain,
and completion paths; it is not the queue count. The operation ingress,
product-level meaning of `0xbb02`, remaining selector targets, absolute dynamic
storage object, callback owner behind `*(0xa07b81a0)`, wire-level completion,
and runtime reachability remain unresolved.

A useful result now identifies the owner of `*(0xa07b81a0)` after the `0xbb02`
drain and the authenticated operation ingress that supplies the selector or
record reaching that callback. Resolving another valid selector's producer or
the absolute dynamic storage object reached by the established 12-byte copy
path is also useful. Do not infer operation names or wire completion from
record layout alone.

## Resolve block 1's delegated materializer

The 69-record block-1 layout and its three block-0 materializer paths are now
established. The data also has a 34-resource UTF-16LE localization bundle, a
matching fixed-width name table, a 239-entry affine descriptor index, 34
monotonic tables, and authenticated coverage for 374 token-bearing strings.
Record 0 supplies source `0x42700800`, length `0x547c00`, decoded image offset
`0x7e0`, and a request that remains conditional on `a3 == 0`. One observation
at delegated service `0x402e90bc` would distinguish copy/DMA from address
mapping and begin to connect these file-relative structures to a parser or
renderer. Broad rescans of block 1 are no longer the smallest useful step.

## Find block 2's consumer

The candidate `(0x00240000, 0x43d00400)` header, `0xff` boundaries, and exact
`0x240000`-byte low-six-bit payload geometry are authenticated. Direct text,
conventional six-bit packing, named compression/transform signatures, exact
cross-block copies, and canonical direct operands did not identify a consumer;
the original container headers are absent from the decoded blocks. The next
useful result is a bounded computed, indirect, runtime-built, or emulated path
that receives the decoded block and establishes what the two header words and
payload mean.

## Find the block 3 resource consumer

Block 3 is now structurally mapped as an eight-entry index followed by eight
contiguous prefixed baseline-JFIF JPEG records and a zero tail. The exact JPEG
extents and dimensions are established, but the index-field meanings and
firmware consumer are not.

A useful result binds one index entry or 16-byte record prefix to an
authenticated block-0 read, copy, decode, or display path. Visual similarity,
address-shaped words, or a guessed UI role without a consumer edge is not
enough.

## Identify decoded block 4's external owner

Block 4 is classified as a flat big-endian H8-compatible image, with an
internal 420-byte source-to-runtime copy/call relationship and a bounded
70-entry dispatch consumer. Its `E. Munch` literal at block-4 offset `0x34`
also appears uniquely at block-0 offset `0x00338a80` immediately before
firmware-update and ID-check text. Additional authenticated ranges reach the
common dispatch target at offset `0x122a`, but conflicting H8 decodes mean no
block-4 instruction semantics are canonical. This narrows the search but still
does not identify an external owner.

A useful result first provides one independently reproducible H8 decode for
the common target at offset `0x122a`, then traces the producer of selector
`0x004003c1`. Following the surrounding block-0 structure at `0x00338a80` to a
fifth-body descriptor, transfer, or start operation remains useful after that
decoder boundary is established. Repeating the string match alone is not
useful.

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
firmware-only. Keep one durable frontier per established boundary rather than
mirroring private campaign cards or live queue state. Coordination and
temporary ownership belong in GitHub issues or PRs, not in this file.
