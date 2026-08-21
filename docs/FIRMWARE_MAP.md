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
| 0 | 9,276 authenticated ranges and 39,415 reviewed MN103 instruction rows |
| 1 | 6 authenticated ranges; no reviewed instructions yet |
| 2 | 2 authenticated ranges; no reviewed instructions yet |
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

The downstream object relationships are narrower but now explicit. The
singleton constructor binds `root+52 = root+276`; the embedded object at
`root+276` receives dispatch word `0x6eef8128`; and the transfer at
`0x40aba1aa` is mechanically `calls *(*(root+52))`. A separate relationship
copies the collection at `outer+132` into `outer+24` and an alias at
`(outer+248)+24`; wrapper `0x40aba091` passes `outer+24` to collection routine
`0x40aac8b4`, which can append the pointer to a dynamic array.

Neither runtime dispatch table `0x6eef8128` nor `0x6eefb4a0` is mapped to
static source bytes. Consequently the exact caller/class and any frame,
display, DMA, or export effect remain unresolved.

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

The remaining boundary is deliberately narrow. The evidence does **not** yet
establish:

- the record’s complete later contents or lifetime;
- an operation-code-to-handler mapping;
- the absolute dynamic transport object or wire-level completion;
- runtime reachability of this path in a specific camera state.

The commands needed to reproduce and extend these windows are in
[ANALYSIS.md](ANALYSIS.md). The remaining boundaries are tracked in
[RESEARCH.md](RESEARCH.md).

The same module now has three additional bounded relationships:

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

Adjacent word `0xa07b82d0` has a direct setter and is later used as the
unsigned dividend of a caller-supplied divisor. Its unit and lifecycle are
still unknown; a completion-status meaning is unsupported.

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

## Decoded block 2 boundary

Block 2 begins with candidate words `0x00240000` and `0x43d00400`; the
candidate payload is exactly `0x240000` bytes at offset `0x3e0`. Unlike
blocks 1 and 3, it does not use the proved `(source, length, 0, 0)` grammar,
and no external consumer or accepted instruction literal binds the candidate
destination. Treating the pair as `(length, destination)` remains a bounded
structural hypothesis, not an admitted loader edge.

## Decoded block 4 classification

The fully authenticated 65,536-byte block 4 is a flat big-endian H8-family
image containing vector-like entries, code, tables, strings, and padding. Its
startup-shaped routine copies block-4 source interval `0xe60e..0xe7b2` (420
bytes) to runtime `0x00400650..0x004007f4` and calls the copied entry. Internal
absolute references agree with relocation delta `0x003f2042`.

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
