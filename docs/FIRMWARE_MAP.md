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
| 0 | 12,943 authenticated ranges and 51,106 reviewed MN103 instruction rows |
| 1 | 827 authenticated ranges; no reviewed instructions yet |
| 2 | 4 authenticated ranges; no reviewed instructions yet |
| 3 | 35 authenticated ranges; no reviewed instructions yet |
| 4 | 3,230 authenticated ranges covering the full 65,536-byte decoded block; no reviewed instructions yet |

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

A separate startup control word at `0x600011d0` now has a bounded setter at
`0x402c0707`, followed by a far return. The startup-adjacent sequence at
`0x402c02b6..0x402c02bc` supplies `-1` and calls that setter; the same word is
read by the branch at the front of the delegated service below `0x402c15d1`.
This establishes one static write/read relationship, not the word's complete
lifecycle or runtime meaning.

An exhaustive block-0 census found no full-width literal or supported direct
PC-relative edge naming initializer `0x402c0262`. The nearby early sequence now
has an authenticated local-overlay handoff: at block-0 offset `0x000000c9` /
runtime `0x6e6000a9` it loads `0x6e6016a2` and jumps indirectly. That target is
backed by block-0 offset `0x000016c2` and begins by clearing `d2`. This closes
the local target mapping, but it still does not connect the handoff to reset or
to initializer `0x402c0262`. The bounded negative does not exclude another
block, ROM, runtime-built state, or a different block-0 address relation.

### Still-corridor singleton dispatch

The indirect calls at `0x40963771` and `0x409637d1` both load slot `+4` from
the table of the singleton stored at runtime global `0x60358c3c`. Its
constructor installs table address `0x6ee69030`. All eight table slots and the
corresponding target source spans now have authenticated coverage; slot `+4`
remains the slot tied directly to these two reviewed callers.

A local relocation relation is established by the 27-entry table at runtime
`0x6ee691d0` / block-0 offset `0x00867db0`: every entry's name pointer maps to
the adjacent NUL-terminated string under the same delta `0x6e601420`. That
relation places the singleton table at offset `0x00867c10`; slot `+4` contains
runtime target `0x6ebdb422`, backed by source offset `0x005da002` (low-view
disassembly address `0x40899fe2`).

For the non-null argument constructed on these caller paths, the target's
predicate sequence selects tag `11780` and directly calls `0x4089a625`. The
accepted corridor continues through object creation and initialization,
associates the incoming values, and appends into the searched list through
`0x4089a73b`. The list's runtime class and later slot-`+20` dispatch remain
runtime-dependent. This establishes a static population path, not shutter
actuation, sensor exposure, image production, or file creation.

The singleton lifecycle is now bounded beyond construction and dispatch. Its
getter, constructor, destructor body, and cleanup reset all have authenticated
spans; the cleanup path loads and clears global `0x60358c3c`, and the
constructor/destructor evidence uses the same table value `0x6ee69030`.
Direct-call and literal censuses do not exclude indirect writes or prove that
every candidate use is reachable.

A separate object path stores its incoming pointer at owner-relative field
`+2216`, calls slot `+0` through that pointer, reloads the same object, and
calls slot `+8` at `0x409613d8`. Its lazy constructor installs table
`0x6ee8d1d0`; slots `+0`, `+4`, and `+8` resolve to `0x6ec1875c`,
`0x6ee1d507`, and `0x6ee1d553`. The slot-`+8` body performs a guarded one-time
initialization of three words at `0x6065949c` through `0x6ee1b784`, then calls
the same object's slot `+4`. The slot-`+4` body reaches several further
receiver-relative indirect calls, beginning at `0x6ee1d52a`. These object,
table, and target identities differ from the established singleton above; the
nested targets, semantic class, and any downstream relationship to the still
corridor remain unresolved.

### Live-view object lifecycle

The corridor beginning at `0x40ab9dbd` (`block 0`, offset `0x007f9ddd`) is a
reverse-order destructor, correcting its earlier construction label. A direct
call at `0x40ab9e73` targets `0x40aba041`. The authenticated containing span
is:

```text
block=0 offset=0x007f9ddd length=382
sha256=592f4b119e2fa9efc4a4b68db11331e49a85530860a935faed3ba833eb965449
```

The lazy singleton accessor is at `0x40ab9cbd`; its construction path begins at
`0x40ab9ceb`, spans 468 bytes, and has eight authenticated direct callers. The
accepted evidence still does not identify a frame-buffer owner, pixel format,
or display/export consumer.

The downstream object relationships are narrower but now explicit. The
singleton constructor binds `root+52 = root+276`; the embedded object at
`root+276` receives dispatch word `0x6eef8128`; and the transfer at
`0x40aba1aa` is mechanically `calls *(*(root+52))`. A separate relationship
copies the collection at `outer+132` into `outer+24` and an alias at
`(outer+248)+24`; wrapper `0x40aba091` passes `outer+24` to collection routine
`0x40aac8b4`, which can append the pointer to a dynamic array.

Runtime dispatch table `0x6eefb4a0` is mapped to block-0 offset
`0x008fa080`; slot `+0x10` resolves to wrapper `0x40aba091`, closing one table
edge in the collection path. The 16-slot table at runtime `0x6eef8128` is now
authenticated at block-0 offset `0x008f6d08`; slot `+0` conditionally resolves
to `0x6edec9be`. A separate 55-entry pointer structure at runtime `0x6ee3e908`
is authenticated at block-0 offset `0x0083d4e8`. Which slot carries the
`outer+132` collection element, the identity between the provider and its
returned product, and any frame, display, DMA, or export effect remain
unresolved.

The `0x6ee3e908` table head now has two additional bounded relationships. The
helper at `0x6eb7e2d8` stores that value through caller-supplied `a0`, clears
the field at `a0+8`, and returns zero. A separate path beginning with the call
at `0x40aac8d7` to `0x40aaca42` builds a 12-byte temporary with the same
dispatch value, copies two stack words into it, and copies three words to a
caller-provided destination. The destination owner and its relationship to the
live-view collection remain unresolved.

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

The helper at `0x6e70cbf5` is more general than this caller: `a0` is the
destination, the low byte of `d0` is the fill value, and unsigned `d1` is the
count. A bounded direct-caller census found zero-fill uses, one literal-space
fill, and two live-`d0` variable-fill sites. The PTP initializer is therefore
one specialization of a shared byte-fill primitive.

The remaining boundary is deliberately narrow. The evidence does **not** yet
establish:

- the record’s complete later contents or lifetime;
- the upstream owner that supplies the request record to the selector
  dispatcher;
- the consumer that selects the distinct static `0x100e` descriptor row and
  any connection from that row to request admission;
- the absolute dynamic transport object or wire-level completion;
- runtime reachability of this path in a specific camera state.

The commands needed to reproduce and extend these windows are in
[ANALYSIS.md](ANALYSIS.md). The remaining boundaries are tracked in
[RESEARCH.md](RESEARCH.md).

Additional bounded relationships in this module include:

- The request selector dispatcher at `0x6f32d60c` reads the halfword at
  `a1+8`. Its eight numeric arms reach `0x1001` at `0x6f32d683`, `0x1002` at
  `0x6f32d6e4`, `0x1003` at `0x6f32d746`, `0x1004` at `0x6f32d7f3`, `0x1005`
  at `0x6f32d86f`, `0x1006` at `0x6f32d8e6`, `0x1007` at `0x6f32d94f`, and
  `0x1008` at `0x6f32d985`. Reviewed `0x1001`, `0x1002`, `0x1007`, and
  `0x1008` paths construct or publish 12-byte descriptors through
  `0x6e61fd8d`. The `0x1005` path at `0x6f32d891` and the `0x1006` path at
  `0x6f32d8fa`/`0x6f32d900` also load pointer global `0xa07b7058` into address
  registers. This is a static software-dispatch relationship, not proof of
  live request admission, operation meaning, capture, or transport completion.
- The nearest authenticated caller now spans `0x6f32d51a..0x6f32d5f8`. It
  builds stack-local records, calls `0x6e61fc4b`, conditionally calls
  `0x6f32dc63`, then passes the stack-derived `a2` as selector argument `a1`
  and `d2` as selector argument `d0`. Under this caller's local source relation,
  `0x6f32dc63` maps to block-0 offset `0x00d2dc83` and is a 33-byte status
  adapter: it writes two words through `a0`, calls `0x6e61fd33`, conditionally
  calls `0x6e682eea` for a negative status, and returns the original status in
  `d0`. Other accepted source spans carry the same runtime address under
  different local views and do not identify this caller's target body.
- `0x6e61fc4b` has two direct calls to the complete 32-byte routine at
  `0x6e689567`. That routine sets `a0=d2` before calling the complete 85-byte
  body at `0x6e6861ea`. The body writes zero to `a0+64`, initializes several
  other fields, links two pointer fields, conditionally calls `0x6e6860f7`,
  then calls `0x6e687d3c` and returns. The caller's later read of `d2+64`
  therefore observes the established zero initialization before it calls
  `0x6e68419f`. The pointed-to object owners, direct-callee contracts, and any
  join to a transport receive path remain unresolved.
- A separate authenticated table at block-0 offset `0x0008f0e0` contains 17
  contiguous 28-byte records keyed by `0x1001`, `0x1002`, and
  `0x100b..0x1019`. Positional word `+12` is consistently target-shaped:
  rows 2 through 12 share `0x6e69e7cb`, while the remaining rows have bounded
  target spans under the same local relation. The `0x100e` row's seven words
  are `(0x100e, 0, 3, 0x6e69e7cb, 5, 0x1000, 0)`. The shared target calls
  `0x6e69d892`, clears the word through `a2`, then dispatches indirectly
  through slot `+20` of an object reached from `d2+24`. Newly authenticated
  neighboring lookup families do not identify the consumer. Reviewed
  local-overlay routines select between four-byte-indexed bases `0x6e68ef1c`
  and `0x6e690a50` under global `0x8050`; other routines first consume distinct
  16- and 20-byte families around `0x6e690708` and `0x6e69081c`. Their geometry
  is incompatible with the 28-byte records, while the separate 34-word vector
  at block-0 offset `0x00090a98` still has no authenticated code reference. No
  runtime owner selects the 17-record table, so it does not add a `0x100e` arm
  to the primary selector or prove request admission.
- A caller-side branch at `0x6f32d597` reaches `0x6f32d9dc`; within it,
  `0x6f32d9f8` directly calls the bounded routine at
  `0x6f32da3f..0x6f32daca`. That routine loads the pointer at `0xa07b702c`
  and calls it indirectly at `0x6f32dab1`. The setup sequence stores
  `0xa07b7044` in pointer global `0xa07b7058`, so the status-3 path's store of
  firmware-resident receiver `0x6f3581f0` at record field `+12` resolves
  statically to `0xa07b7050`; the same receiver is later passed as callback
  context. Three additional direct reads of `0xa07b7058` are established in
  the selector arms above. This is an owner-side static alias and continuation;
  allocation, runtime ordering, scheduling, live ingress, and response behavior
  remain unproved.
- `0x6f330fba` appends 16-byte records to the array beginning at
  `0xa07b81cc`; `0x6f3307f5` consumes the front record and compacts the
  remainder. The halfword at `0xa07b82cc` is the live count for at most 16
  records, not a completion flag.
- The same consumer calls `0x6f33093e`; when global `0x8050` is nonzero, its
  helper builds a stack descriptor with a size word of 128 and passes it
  through `0x6e61fd8d` to the dynamic storage routine at `0x6e68939a`. The
  fixed path then uses record `+8` as a sequence value, advances it modulo 16,
  and probes 16 eight-byte slots in `[0x6f358d44,0x6f358dc4)`. Each matching
  slot holds the full sequence at `+0` and a handler at `+4`; control stops at
  the indirect jump at `0x6f3309c6`. The apparent same-view source coordinate
  `0x00d58d44` is authenticated non-table data, and the static dispatch records
  at `0x00d589f8` are a distinct structure. Paired routines at `0x6e681503` and
  `0x6e68150d` write `d1` at `a0+20+8*d0` and `a0+24+8*d0`; their established
  callers supply both fields for the same indices. This geometry is compatible
  with the 16-slot table if the incoming base is `0x6f358d30`, but no accepted
  instruction establishes that alias or its runtime owner. This proves a
  candidate materializer shape, not table ownership, serialization, endpoint
  submission, DMA, or wire completion.
- The complete containing initializer spans `0x6f32f6b5..0x6f32f864`; its
  suffix at `0x6f32f824..0x6f32f862` directly calls
  `0x6f3391d0` at `0x6f32f848` and `0x6f33c8f5` at `0x6f32f856`. The first
  path writes `0x6f33aa63` to `0xa07b702c` through setter `0x6f32d5f8`;
  the second writes `0x6f33e38f` to separate global `0xa07b7030` through
  `0x6f32d602` and installs `0x6f33e485` into `0xa07b81a0`. The reviewed
  `0x6f33e38f` entry fixes `d2` and its return value at 24, reaches helper
  `0x6e6050e5`, and returns through a 32-byte cleanup; the helper's nonzero
  `0x8050` path builds a size-128 descriptor and hands it to `0x6e61fd8d`.
  This differs from the record-populating shape of `0x6f33aa63`; adjacent
  registration does not prove a shared callback signature. The last target
  `0x6f33e485` instead tests caller-supplied `d2`, conditionally reaches a
  diagnostic-looking helper, and returns `d2`. Canonical block-0 instruction
  rows contain no direct load of `0xa07b7030`; runtime ordering and ownership,
  the contract installed through `0xa07b702c`, and any indirect or runtime-built
  consumer of `0xa07b7030` remain unresolved. PTP namespace constants and local
  labels support a PTP-adjacent module attribution, but no RTOS task entry or
  operation-code ingress is established.
- On the out-of-range-selector path, `0x6f33113f` uses record `+0` as a
  dynamic handle and constructs a 12-byte stack payload from the input
  halfword tag plus record fields `+4` and `+12`. It passes that payload
  through `0x6e61fd8d` to `0x6e68939a`, which copies it into dynamic queued or
  circular storage. Bytes 2 and 3 are not initialized by the builder. This
  proves a buffer-copy path, not USB/wire completion.
- Accepted coverage continues the storage corridor at `0x6e6893ae` through a
  pointer walk rooted at table `0x8ff00004`. The current `0x8050` value selects
  an owner; reviewed rows then read the queue pointer at owner `+0x3c` and its
  unsigned halfword bound at queue `+0x1a`. A source-only leaf at block-0
  offset `0x000a9736` can store incoming `a1` at owner `+0x3c`, but its runtime
  address, caller, and the queue allocation are unresolved. These are static
  storage and field-level boundaries, not an operation ingress or a wire-level
  completion proof.
- A late handler span at `0x6f33fb8e` has an authenticated direct call to
  `0x6f33faec` followed by a return, and the established incoming load maps a
  selected vector tail into that span. This adds a static handler boundary,
  not runtime reachability, operation meaning, or wire-level completion.
- A 66-record table at block-0 offset `0x0008b300` uses 28-byte records. Its
  key-`0x4e` record points to `0x6e708fa2`, three bytes into the authenticated
  body at `0x6e708f9f` and exactly at the reviewed call to `0x6f33f6dc`.
  Two other raw four-byte hits near that body are alignment false positives:
  bytes `6e 70 90 82` at block-0 offset `0x003a312f` begin inside a
  little-endian vector word, while bytes `6e 70 90 08` at `0x0081422a`
  cross three MN103 instructions in GNU objdump 2.45's decode of the enclosing
  range. This leaves one static table-to-interior-entry edge; no accepted
  evidence identifies the table's runtime address, owner, selection logic, or
  indirect invocation.
- The uncovered byte starts at `0x6f331e20`, `0x6f331e30`, and `0x6f331e58`
  independently decode as `clr d0`, `clr d0`, and `clr d1`. They are alternate
  starts at byte gaps between retained canonical rows; no accepted branch,
  table, or caller selects them. These decodes do not establish entry identity,
  runtime reachability, or handler execution.

The five reviewed `0xbb02` literal sites now establish one bounded reply
lifecycle: a 16-byte request layout, selector dispatch through record `+8`,
normal FIFO compaction, an exceptional tail-pop drain, 12-byte reply packing,
and an unsigned-halfword return. The tag's product-level name and wire-level
completion remain unproved.

Nearby routines `0x6f334b0e` and `0x6f334b37` form a two-entry static buffer
pool. Checkout first-fit reserves one of two `0x40000`-byte backing buffers and
returns its pointer or null; release matches that pointer and clears the
descriptor's availability halfword. Routine `0x6f334b5e` is a separate
stateful consumer, not another release primitive.

Adjacent halfword `0xa07b82d0` is co-reset with the FIFO and is later used as
the unsigned dividend of a caller-supplied divisor. It is not referenced by
the reviewed append, shift, drain, or completion paths, while the FIFO has a
separate count halfword. Its unit and lifecycle remain unknown; queue-count or
completion-status meanings are unsupported.

## Decoded block 1 materialization

Block 1 begins with 69 contiguous 16-byte `(source, length, 0, 0)` records,
followed by zero padding to offset `0x7e0` and 69 corresponding data images.
The sources cover `0x42700800..0x42fb9400`, and each data image begins at
decoded offset `source - 0x42700020`. The combined payload ends at offset
`0x8b93e0`; the remainder is zero.

Block-0 code installs the block-1 table view and indexes those records by 16.
Three materializer paths use default destinations `0xaf966000`, `0xaff7d000`,
and `0xaff21000`. Their common helper receives source, destination, length, and
attribute `0x0101`, then delegates the actual service below `0x402e90bc`.
Static evidence therefore establishes the record and request relationship but
does not distinguish copying, DMA, or address mapping inside that service.

Record 0 is now bounded as source `0x42700800`, length `0x547c00`, decoded
image offset `0x000007e0`; its common-service request remains conditional on
`a3 == 0`. Records 2, 14, 20, 29, 34, 45, and 46 also have authenticated
conditional materializer paths. None of these paths establishes the delegated
service's transfer effect.

Accepted rows now extend the selector setup across block-0 offsets
`0x00257798..0x00257817`: the selector is zero-extended, scaled by the
16-byte record width, added to a table base, and used with record and global
state before a helper call. One authenticated high view places that call at
`0x6e8577f7` with target `0x6e857d27`. The same source corridor has competing
runtime views, so this does not select one authoritative mapping or establish
the delegated service's copy, DMA, mapping, parsing, or rendering effect.

The materialized data has two additional verified structures. One is a
34-resource, directory-aligned UTF-16LE string-dictionary bundle with a
matching fixed-width 34-name table and repeated `@A000@..@A0EE@` token family.
The other is a 239-entry affine descriptor index whose back-pointers and
reserved-zero fields reproduce, alongside 34 strictly monotonic tables.
Canonical coverage now authenticates 523 additional block-1 directory,
record, and localization spans, including 374 token-bearing strings across the
34 resources and bounded repeated token families. Per-resource runtime
population, compact-family geometry, token-to-glyph meaning, and the consumers
of those tables remain unresolved.

## Decoded block 2 boundary

Block 2 begins with candidate words `0x00240000` and `0x43d00400`. Its exact
physical partition is now established: the 8-byte prefix, `0xff` fill through
offset `0x3e0`, a `0x240000`-byte payload through `0x2403e0`, and trailing
`0xff` fill through block end. The first word equals the payload length. The
payload uses byte values `0x00..0x3f` except `0x3c`; bounded scans rejected the
named conventional six-bit packings, compression signatures, simple
delta/scrambling transforms, and direct text encodings.

Unlike blocks 1 and 3, block 2 does not use the proved
`(source, length, 0, 0)` grammar. No exact external copy or canonical
instruction operand identifies a consumer, and the original container headers
are absent from the decoded blocks.

A new block-0 static parameter path begins with the call at `0x405174b4` to
`0x40517d27`. For selector `0x101`, the reproduced helper path chooses mask
`0x1ff` and normalizes `a0=0x43d00400`, `a1=0x43d00000`, `d0=0x400`, and
`d1=0x101`; `0x43d00000 + 0x400` equals the second block-2 header word. This
connects the header values to a materializer-shaped parameter path but stops
before the delegated call at `0x40517d60`. It does not prove payload access,
copying, DMA, mapping, or runtime reachability.

## Decoded block 3 resource bundle

Block 3 has an eight-entry candidate index at offsets `0x00000000..0x00000080`
and eight contiguous prefixed records beginning at `0x000003e0`. Each record
contains one complete, independently parsed baseline JFIF JPEG; the JPEG spans
do not overlap, bytes after each EOI through the next record boundary are zero,
and the remainder from `0x003949e0` through block end is zero. All non-JPEG
nonzero bytes outside the payloads are confined to the index and 16-byte
record prefixes.

This establishes a static eight-image resource bundle and exact JPEG extents,
not the meanings of the prefix words or address-like index fields. No accepted
code consumer, runtime owner, or UI/compositing role has been established.

## Decoded block 4 classification

The fully authenticated 65,536-byte block 4 is a flat big-endian H8-compatible
image containing vector-like entries, code, tables, strings, and padding. Its
startup-shaped routine copies block-4 source interval `0xe60e..0xe7b2` (420
bytes) to runtime `0x00400650..0x004007f4` and calls the copied entry. Internal
absolute references agree with relocation delta `0x003f2042`.

A bounded consumer at `0xd316..0xd375` indexes a 70-entry dispatch table at
`0xe898..0xe9b0`, within a larger aligned big-endian target-table region. An
eight-byte `E. Munch` literal at block-4 offset `0x34` also occurs uniquely at
block-0 offset `0x00338a80`, immediately before firmware-update and ID-check
text. The byte identity and context are exact, but they do not establish a
descriptor, transfer, owner, or start edge.

Additional authenticated ranges cover H8-shaped handler and target windows
from block-4 offset `0x05b8` through `0xe94c`, including the common dispatch
target at `0x122a`. No block-4 instruction row is canonical: conflicting H8
decodes remain unresolved, so the new coverage authenticates source structure
without choosing instruction semantics.

This establishes an internal materialization relationship. It does not yet
establish the exact H8 chip, external block-4 loader, hardware owner, reset
reachability, or a block-0 consumer.

## Host-visible container integrity

The reference unpack/repack model reconstructs the official image
byte-identically. In a reproduced nonempty test, changing decoded block-4
offset 0, rescrambling the body, and updating the additive tail checksum
produced a same-size five-block image accepted by that host parser; the
unrepaired control failed its checksum. The exact-source verifier correctly
rejects the modified image because it is not the registered research source.

This proves only the regular container transformation and checksum boundary.
Updater validation, transfer acceptance, device-side checks, loading,
authentication, and successful boot remain unknown.
