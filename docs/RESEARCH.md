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
- still capture around `0x409613d8` and `0x4096368d`;
- live-view teardown around `0x40ab9dbd` and wrapper `0x40aba091`;
- PTP selector handling around `0x6f32d60c` and record handling around
  `0x6f3307f5`.

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

A separate accepted path stores an object at owner-relative field `+2216`,
calls its slot `+0`, reloads it, and calls slot `+8` at `0x409613d8`. This is a
distinct lazy object with table `0x6ee8d1d0`; slot `+0` resolves to
`0x6ec1875c`, slot `+4` to `0x6ee1d507`, and slot `+8` to `0x6ee1d553`. The
slot-`+8` body performs a guarded initialization of `0x6065949c` and, for this
established object identity, its call at `0x6ee1d583` resolves back to slot
`+4`. The useful next boundary is now the slot-`+4` body's nested receiver call
at `0x6ee1d52a` or its later slot-`+72`/`+76` calls. Identify those concrete
receivers and targets, then test whether either joins the established singleton
corridor. The static calls alone do not prove capture or hardware behavior.

## Identify the live-view frame owner

The lazy singleton accessor at `0x40ab9cbd` constructs through `0x40ab9ceb`;
the corridor beginning at `0x40ab9dbd` is its reverse-order destructor, not
its constructor. Dispatch table `0x6eefb4a0` is mapped, with slot `+0x10`
resolving to wrapper `0x40aba091`; the 16-slot table `0x6eef8128` is now mapped
too, with slot `+0` conditionally resolving to `0x6edec9be`. No frame-buffer
owner, format, or display/export consumer is established. Previous exact
string-address scans did not produce an instruction-aligned owner reference,
so another vocabulary scan is unlikely to help.

Accepted coverage now also ties table head `0x6ee3e908` to the bounded helper
at `0x6eb7e2d8` and to a 12-byte temporary/three-word copy path reached through
`0x40aac8d7`. A useful result identifies the owner of that helper's
caller-supplied object or the destination of the three-word copy, then binds it
to the `outer+132` collection or one concrete frame handle. The lifecycle,
object binding, collection append, and mapped tables are already established.

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
storage object, wire-level completion, and runtime reachability remain
unresolved. The callback value installed in `0xa07b81a0` is now statically
identified as `0x6f33e485` through initializer `0x6f33c8f5`, with a direct call
to that initializer at `0x6f32f856`. The complete containing initializer is
now bounded at `0x6f32f6b5..0x6f32f864`; its runtime owner and the meaning of
the callback's caller-supplied `d2` value are still unresolved.

The fixed FIFO consumer now has a bounded internal handoff on its nonzero
`0x8050` branch: a helper builds a stack descriptor with size word 128, passes
it through `0x6e61fd8d` to storage at `0x6e68939a`, and later stops at the
record-`+8`-selected indirect jump at `0x6f3309c6`. The selector is a full
sequence value; the consumer advances it modulo 16 and probes 16 eight-byte
slots in `[0x6f358d44,0x6f358dc4)`, comparing slot `+0` and loading the target
from slot `+4`. The same-view source coordinate `0x00d58d44` is authenticated
non-table data, so the table remains runtime-built or supplied through another
unproved mapping. Paired routines at `0x6e681503` and `0x6e68150d` write the
two fields of an eight-byte-stride array at base-relative offsets `+20` and
`+24`. Their established callers populate both fields for matching indices,
but no accepted instruction proves that their incoming base is `0x6f358d30`.
A useful continuation establishes that base provenance and runtime owner before
resolving an indirect target. The present evidence does not establish table
ownership, serialization, or wire completion.

A separate request-selector corridor is now authenticated at `0x6f32d60c`.
It reads the selector from `a1+8` and dispatches each value from `0x1001`
through `0x1008` to a distinct target. Reviewed `0x1001`, `0x1002`, `0x1007`,
and `0x1008` paths reach the 12-byte descriptor handoff at `0x6e61fd8d`; this
establishes a shared static response boundary, not live request admission or
wire completion. The `0x1005` arm at `0x6f32d891` and `0x1006` arm at
`0x6f32d8fa`/`0x6f32d900` now also have reviewed loads of owner pointer global
`0xa07b7058`. The recovered switch still does not establish a `0x100e` arm.

A separate authenticated table at block-0 offset `0x0008f0e0` consists of 17
28-byte records keyed by `0x1001`, `0x1002`, and `0x100b..0x1019`. Its
`0x100e` row contains positional words
`(0x100e, 0, 3, 0x6e69e7cb, 5, 0x1000, 0)`. A locally supported code view of
`0x6e69e7cb` reaches an owner-relative indirect call. Positional word `+12`
is now bounded as the common target field across the record family, but no
authenticated consumer selects the table. A nearby four-byte indexed pointer
lookup has incompatible geometry. Newly reviewed local-overlay routines pair
that four-byte base with `0x6e690a50` under `0x8050`, while other routines use
distinct 16- and 20-byte families around `0x6e690708` and `0x6e69081c`; none
selects the 28-byte record table. A separate 34-word vector at block-0 offset
`0x00090a98` still has no authenticated code reference. The table therefore
narrows the alternate `0x100e` path question without proving registration,
request admission, or a native response.

The nearest authenticated caller is now complete at
`0x6f32d51a..0x6f32d5f8`. It builds stack-local records, first calls
`0x6e61fc4b`, conditionally passes the stack-derived object through
`0x6f32dc63`, and then supplies that object as selector `a1`. The caller's
local source relation now identifies a 33-byte `0x6f32dc63` status adapter at
block-0 offset `0x00d2dc83`: it writes two record words, calls `0x6e61fd33`,
conditionally calls `0x6e682eea` after a negative status, and returns that
status. This closes the caller-side adapter ABI while leaving its runtime owner
and any join to the known FIFO or transport receive path unresolved.

The `0x6e61fc4b` path also has two direct calls to a complete routine at
`0x6e689567`. That routine sets `a0=d2` before calling the complete 85-byte
body at `0x6e6861ea`, which writes zero to `a0+64`, initializes other fields,
links pointer fields, conditionally calls `0x6e6860f7`, then calls
`0x6e687d3c` and returns. The later read of `d2+64` therefore observes the
proved zero initialization. The next bounded question on this branch is the
contract of `0x6e6860f7` on the bit-1-set path or the runtime owner of the
pointed-to objects.

A separate caller-side continuation now runs
`0x6f32d597 -> 0x6f32d9dc -> 0x6f32d9f8 -> 0x6f32da3f` and stops at the
indirect call through global `0xa07b702c` at `0x6f32dab1`. The initializer
sequence `0x6f32f824..0x6f32f862` can install `0x6f33aa63` into that global
and `0x6f33e38f` into sibling global `0xa07b7030`. The setup writes
`0xa07b7044` into pointer global `0xa07b7058`, so the continuation's status-3
store of fixed firmware receiver `0x6f3581f0` at record `+12` resolves to
`0xa07b7050`; the same receiver is later passed as callback context. Three
additional selector-arm reads of the pointer global are now reviewed, but no
allocation, scheduler, or runtime ordering is established.

The sibling target `0x6f33e38f` now has a bounded fixed-status entry: it sets
`d2=24`, reaches `0x6e6050e5`, and returns 24. The helper's nonzero-`0x8050`
path builds a size-128 descriptor and reaches `0x6e61fd8d`. This entry shape is
not interchangeable with the record-populating `0x6f33aa63` shape, and the
canonical block-0 instruction rows contain no direct load of `0xa07b7030`.
The containing initializer's runtime owner and ordering, the receiver's type,
the contract reached through `0xa07b702c`, and any indirect consumer of the
sibling global remain unproved.

The storage corridor at `0x6e6893ae` now has a field-level owner relation:
`0x8050` indexes the owner table at `0x8ff00004`, the selected owner's `+0x3c`
field supplies a queue pointer, and queue `+0x1a` supplies an unsigned bound.
A source-only leaf at block-0 offset `0x000a9736` can store an incoming pointer
at owner `+0x3c`, but its runtime address, caller, and the queue allocation are
not established. A useful result identifies that writer's authenticated caller
and the concrete object supplied in `a1`.

The highest-leverage next direction is to prove whether the paired field
writers receive base `0x6f358d30`, then identify that object's runtime owner
before resolving the target selected at `0x6f3309c6`. Alternatively, identify
the consumer and runtime owner of the 17-record table and prove whether it
selects the `0x100e` row, or establish the
runtime owner and ordering of the callback initializer and resolve the handler
reached through `0xa07b702c`. Another broad opcode or table scan is not the
smallest next step.

A useful result now joins one of those exact owners or consumers to an
authenticated transport receive boundary. Resolving the absolute dynamic
storage object reached by the established 12-byte copy path is also useful.
Do not infer operation names or wire completion from record layout alone.

The late handler at `0x6f33fb8e` now has a reviewed direct call to
`0x6f33faec` and return, with an established incoming load mapping a selected
vector tail into the span. The useful next step is its authenticated producer
or runtime owner, not another isolated decode of the handler body.

## Resolve block 1's delegated materializer

The 69-record block-1 layout and its three block-0 materializer paths are now
established. The data also has a 34-resource UTF-16LE localization bundle, a
matching fixed-width name table, a 239-entry affine descriptor index, 34
monotonic tables, and authenticated coverage for 374 token-bearing strings.
Record 0 supplies source `0x42700800`, length `0x547c00`, decoded image offset
`0x7e0`, and a request that remains conditional on `a3 == 0`. One observation
at delegated service `0x402e90bc` would distinguish copy/DMA from address
mapping and begin to connect these file-relative structures to a parser or
renderer. Accepted rows now extend the selector setup across block-0 offsets
`0x00257798..0x00257817`, including 16-byte record scaling and a high-view call
at `0x6e8577f7`, but the same source corridor retains competing runtime views.
The useful next result is an independently anchored complete caller context
that selects the applicable view and follows the request through
`0x402e90bc` to a proved payload effect. Broad rescans of block 1 are no longer
the smallest useful step.

## Find block 2's consumer

The candidate `(0x00240000, 0x43d00400)` header, `0xff` boundaries, and exact
`0x240000`-byte low-six-bit payload geometry are authenticated. Direct text,
conventional six-bit packing, named compression/transform signatures, exact
cross-block copies, and canonical direct operands did not identify a consumer.
A new static parameter path ties selector `0x101` to
`a0=0x43d00400`, `a1=0x43d00000`, length `0x400`, and attribute `0x101`, so
the base plus length reproduces the second header word. It stops before the
delegated call and does not access the payload. The next useful result follows
that exact boundary into a proved payload read, copy, mapping, or consumer
effect without treating the parameter equality itself as consumption.

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
