# Decoded blocks and container integrity

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

The five decoded blocks have different structures. The overview and coverage
counts are in the [map](../FIRMWARE_MAP.md#current-coverage); this page records
the detailed data layouts and their known consumers. Source structure, code
display addresses, and runtime placement remain distinct.

- [Block 1: records and materialization requests](#block-1)
- [Block 2: payload boundaries and candidate parameters](#block-2)
- [Block 3: JPEG resource bundle](#block-3)
- [Block 4: H8-compatible image](#block-4)
- [Host-visible container integrity](#container-integrity)

<a id="block-1"></a>
## Block 1: records and materialization requests

Block 1 begins with 69 contiguous 16-byte `(source, length, 0, 0)` records,
followed by zero padding to offset `0x7e0` and 69 corresponding data images.
The sources cover `0x42700800..0x42fb9400`, and each data image begins at
decoded offset `source - 0x42700020`. The combined payload ends at offset
`0x8b93e0`; the remainder is zero.

Block-0 code installs the block-1 table view and indexes those records by 16.
Three materializer paths use default destinations `0xaf966000`, `0xaff7d000`,
and `0xaff21000`. Their common helper receives source, destination, length,
and attribute `0x0101`, then delegates the actual service below `0x402e90bc`.
Static evidence therefore establishes the record and request relationship but
does not distinguish copying, DMA, or address mapping inside that service.

Record 0 is bounded as source `0x42700800`, length `0x547c00`, decoded image
offset `0x000007e0`; its common-service request remains conditional on
`a3 == 0`. Records 2, 14, 20, 29, 34, 45, and 46 also have authenticated
conditional materializer paths. None of these paths establishes the delegated
service's transfer effect.

The supported selector setup spans block-0 offsets `0x00257798..0x00257817`:
the selector is zero-extended, scaled by the 16-byte record width, added to a
table base, and used with record and global state before a helper call. One
authenticated high view places that call at `0x6e8577f7` with target
`0x6e857d27`. The same source corridor has competing runtime views, so this
does not select one authoritative mapping or establish the delegated service's
copy, DMA, mapping, parsing, or rendering effect.

The materialized data contains two verified structures. One is a 34-resource,
directory-aligned UTF-16LE string-dictionary bundle with a matching fixed-width
34-name table and repeated `@A000@..@A0EE@` token family. The other is a
239-entry affine descriptor index whose back-pointers and reserved-zero fields
reproduce, alongside 34 strictly monotonic tables. Authenticated directory,
record, and localization spans include 374 token-bearing strings across the 34
resources and bounded repeated token families. Per-resource runtime population,
compact-family geometry, token-to-glyph meaning, and the consumers of those
tables remain unresolved.

**Next evidence:** [Resolve block 1's delegated
materializer](../RESEARCH.md#r-block-1).

<a id="block-2"></a>
## Block 2: payload boundaries and candidate parameters

Block 2 begins with candidate words `0x00240000` and `0x43d00400`. Its exact
physical partition is established: the 8-byte prefix, `0xff` fill through
offset `0x3e0`, a `0x240000`-byte payload through `0x2403e0`, and trailing
`0xff` fill through block end. The first word equals the payload length. The
payload uses byte values `0x00..0x3f` except `0x3c`; bounded scans rejected
the named conventional six-bit packings, compression signatures, simple
delta/scrambling transforms, and direct text encodings.

Unlike blocks 1 and 3, block 2 does not use the proved `(source, length, 0, 0)`
grammar. No exact external copy or canonical instruction operand identifies a
consumer, and the original container headers are absent from the decoded
blocks.

A block-0 static parameter path begins with the call at `0x405174b4` to
`0x40517d27`. For selector `0x101`, the reproduced helper path chooses mask
`0x1ff` and normalizes `a0=0x43d00400`, `a1=0x43d00000`, `d0=0x400`, and
`d1=0x101`; `0x43d00000 + 0x400` equals the second block-2 header word. This
connects the header values to a materializer-shaped parameter path but stops
before the delegated call at `0x40517d60`. It does not prove payload access,
copying, DMA, mapping, or runtime reachability.

**Next evidence:** [Find block 2's consumer](../RESEARCH.md#r-block-2).

<a id="block-3"></a>
## Block 3: JPEG resource bundle

Block 3 has an eight-entry candidate index at offsets `0x00000000..0x00000080`
and eight contiguous prefixed records beginning at `0x000003e0`. Each record
contains one complete, independently parsed baseline JFIF JPEG; the JPEG spans
do not overlap, bytes after each EOI through the next record boundary are zero,
and the remainder from `0x003949e0` through block end is zero. All non-JPEG
nonzero bytes outside the payloads are confined to the index and 16-byte record
prefixes.

This establishes a static eight-image resource bundle and exact JPEG extents,
not the meanings of the prefix words or address-like index fields. No accepted
code consumer, runtime owner, or UI/compositing role has been established.

**Next evidence:** [Find the block 3 resource
consumer](../RESEARCH.md#r-block-3).

<a id="block-4"></a>
## Block 4: H8-compatible image

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

Authenticated ranges cover H8-shaped handler and target windows from block-4
offset `0x05b8` through `0xe94c`, including the common dispatch target at
`0x122a`. No block-4 instruction row is canonical: conflicting H8 decodes
remain unresolved, so these ranges authenticate source structure without
choosing instruction semantics.

This establishes an internal materialization relationship. It does not yet
establish the exact H8 chip, external block-4 loader, hardware owner, reset
reachability, or a block-0 consumer.

**Next evidence:** [Resolve block 4's decoder and external
owner](../RESEARCH.md#r-block-4).

<a id="container-integrity"></a>
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

**Next evidence:** [Establish updater or device
authentication](../RESEARCH.md#r-integrity).
