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
| 0 | 9,490 authenticated ranges and 39,456 reviewed MN103 instruction rows |
| 1 | 183 authenticated ranges; no reviewed instructions yet |
| 2 | 4 authenticated ranges; no reviewed instructions yet |
| 3 | 34 authenticated ranges; no reviewed instructions yet |
| 4 | 3,146 authenticated ranges covering the full 65,536-byte decoded block; no reviewed instructions yet |

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
PC-relative edge naming initializer `0x402c0262`. The nearby early sequence
ends in an indirect handoff through fixed value `0x6e6016a2`, but the supplied
evidence does not map that target back to the initializer. This is a bounded
block-0 negative, not proof that the owner cannot be in another block, ROM, or
runtime-built table.

### Still-corridor singleton dispatch

The indirect calls at `0x40963771` and `0x409637d1` both load slot `+4` from
the table of the singleton stored at runtime global `0x60358c3c`. Its
constructor installs table address `0x6ee69030`.

A local relocation relation is established by the 27-entry table at runtime
`0x6ee691d0` / block-0 offset `0x00867db0`: every entry's name pointer maps to
the adjacent NUL-terminated string under the same delta `0x6e601420`. That
relation places the singleton table at offset `0x00867c10`; slot `+4` contains
runtime target `0x6ebdb422`, backed by source offset `0x005da002` (low-view
disassembly address `0x40899fe2`).

For the non-null argument constructed on these caller paths, the target's
predicate sequence selects tag `11780` and directly calls `0x4089a625`. The
later object/list lookup and virtual dispatch remain runtime-dependent. This
establishes a static tag-selection path, not shutter actuation, sensor
exposure, image production, or file creation.

The singleton lifecycle is now bounded beyond construction and dispatch. Its
getter, constructor, destructor body, and cleanup reset all have authenticated
spans; the cleanup path loads and clears global `0x60358c3c`, and the
constructor/destructor evidence uses the same table value `0x6ee69030`.
Direct-call and literal censuses do not exclude indirect writes or prove that
every candidate use is reachable.

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

Runtime dispatch table `0x6eefb4a0` is now mapped to block-0 offset
`0x008fa080`; slot `+0x10` resolves to wrapper `0x40aba091`, closing one table
edge in the collection path. Dispatch table `0x6eef8128`, the identity between
the provider and its returned product, and any frame, display, DMA, or export
effect remain unresolved.

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
- an operation-code-to-handler mapping;
- the absolute dynamic transport object or wire-level completion;
- runtime reachability of this path in a specific camera state.

The commands needed to reproduce and extend these windows are in
[ANALYSIS.md](ANALYSIS.md). The remaining boundaries are tracked in
[RESEARCH.md](RESEARCH.md).

Additional bounded relationships in this module include:

- `0x6f330fba` appends 16-byte records to the array beginning at
  `0xa07b81cc`; `0x6f3307f5` consumes the front record and compacts the
  remainder. The halfword at `0xa07b82cc` is the live count for at most 16
  records, not a completion flag.
- The initialization chain through `0x6f33c8f5` installs two callback values
  into globals later called by this record module. PTP namespace constants and
  local labels support a PTP-adjacent module attribution, but no RTOS task
  entry or operation-code ingress is established.
- On the out-of-range-selector path, `0x6f33113f` uses record `+0` as a
  dynamic handle and constructs a 12-byte stack payload from the input
  halfword tag plus record fields `+4` and `+12`. It passes that payload
  through `0x6e61fd8d` to `0x6e68939a`, which copies it into dynamic queued or
  circular storage. Bytes 2 and 3 are not initialized by the builder. This
  proves a buffer-copy path, not USB/wire completion.

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

The materialized data has two additional verified structures. One is a
34-resource, directory-aligned UTF-16LE string-dictionary bundle with a
matching fixed-width 34-name table and repeated `@A000@..@A0EE@` token family.
The other is a 239-entry affine descriptor index whose back-pointers and
reserved-zero fields reproduce, alongside 34 strictly monotonic tables.
Per-resource runtime population, compact-family geometry, and the consumers of
those tables remain unresolved.

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
are absent from the decoded blocks. Treating `0x43d00400` as a destination or
load base remains a structural hypothesis; computed, indirect, or
runtime-built consumers are not excluded.

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
