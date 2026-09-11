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
| 0 | 13,000 authenticated ranges and 51,666 reviewed MN103 instruction rows |
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

### Bounded caller source coverage

The 56-byte block-0 range `[0x006b0204,0x006b023c)` extends the existing
48-byte same-start slice through the complete five-byte call at offset
`0x006b0232` and the return at `0x006b0239`. The shorter slice remains valid
range evidence, but its endpoint lies inside that call. This addition
provides a complete source span through the return; it adds no instruction
rows and establishes no event identity, runtime execution, or image transfer.

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
concrete runtime receivers, semantic class, and any downstream relationship to
the still corridor remain unresolved.

The nested call at `0x6ee1d52a` loads receiver-table slot `+12`. The
canonical six-byte range at block-0 offset `0x0081a3a2`, decoded locally at
`0x6ee1b7c2`, is `mov (8,a0),a0` followed by `retf [],0` at `0x6ee1b7c5`.
The return is now a canonical instruction row. The existing load row uses
address `0x6ee1b7c8` for the same source offset; this acceptance does not
replace that anchor or admit an alternate-address load row. Under the local
view, the bounded body is a field getter. Its field meaning, the receiver's
runtime identity, and downstream image ownership remain unproven; this body
does not establish capture actuation or image transfer.

For the established table `0x6ee8d1d0`, slot `+72` resolves to
`0x6ee1d38f` (block-0 offset `0x0081bf6f`, 15 bytes). This wrapper loads
`*(a0)`, calls that receiver table's slot `+64`, and returns. Under the same
table identity, slot `+64` resolves to `0x6ee1d263` (offset `0x0081be43`,
57 bytes). That body branches on `d0`, calls `0x6ee1db5b` on both paths,
uses `0x6ee1b795` and `0x6ee1b7a6` around the zero-input path, and returns
the saved scalar result in `d0`. Both spans and 29 instruction rows are now
canonical; the two-byte boundary at `0x6ee1d281` has range coverage only.
These bodies bound the proposed slot-`+72` continuation but do not prove
runtime dispatch, capture, frame/image creation, file publication, or transfer.

The adjacent slot `+76` maps to `0x6ee1d39e` (block-0 offset
`0x0081bf7e`, 45 bytes). Its now-canonical body prepares a stack temporary
through `0x6ee1b795`, passes it to `0x6ee1db5b`, calls `0x6ee1b7a6`, and
returns the saved result. The direct successor `0x6ee1db5b` (offset
`0x0081c73b`, 103 bytes) also has canonical coverage. After a predicate call
and a conditional slot-`+8` status path, it restores the incoming parent
receiver from `a2` into `a0` and calls that receiver's slot `+52` at
`0x6ee1db7f`. It saves the returned `a0` in `a3`; later dispatch uses the
other incoming object and the returned object, including slots `+8` or `+48`
of the latter according to global `0x6035b1ac`. These 72 instruction rows
establish bounded dynamic dispatch and return mechanics, not the returned
object's ownership, capture, image/file creation, hardware actuation, or an
image consumer.

For parent table `0x6ee8d1d0`, slot `+52` resolves to the already-canonical
six-byte getter at `0x6ee1dc28` (block-0 offset `0x0081c808`): it loads
field `+100` into `a0` and returns. The newly accepted writer at `0x6ee1d588`
(offset `0x0081c168`, nine bytes) stores incoming `a1` into fields `+100`
and `+92`, then returns. This identifies a setter body, not the producer or
concrete dispatch table of the stored object. The same parent table's slot
`+40` resolves to `0x6ee1d727` (offset `0x0081c307`, three bytes), whose
accepted body is only `retf [],0`. That bounded no-op does not identify the
other incoming object's slot-`+40` target at `0x6ee1db91`. The field value,
its runtime provenance, and its later slot-`+8`/`+48` consumers remain
unresolved; none of these bodies establishes image ownership or transfer.

The accepted 26-byte initializer at local address `0x6ec0b717` (block-0
offset `0x0060b2f7`) clears `d0`, sets `a1` to zero, calls `0x6ee1a0ef`,
then writes table value `0x6ee8a59c` through the post-call `a0` and stores
halfword `2204` at `a0+4` before returning. The 160-byte table span at
offset `0x0088a17c` maps to `0x6ee8a59c` under the same local delta
`0x6e600420`. Its slots `+52` and `+56` contain the field-`+100` getter
`0x6ee1dc28` and writer `0x6ee1d588`; slots `+8`, `+64`, `+72`, and `+76`
also share the previously mapped targets. Its slot `+40`, however, contains
`0x6edeeaf7`, so the no-op established for table `0x6ee8d1d0` cannot be
transferred to this table. These source spans establish a separate table
candidate with shared methods. They do not prove the allocator/helper's
behavior, the field-`+100` value's provenance, or the runtime receiver at a
later indirect call. The local address relation is not a global load base.

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

### Candidate receiver method prologue

The five-byte span at block-0 offset `0x007bfce4`, under local address view
`0x6edc1104`, now has two reviewed instructions: `movm [d2,a2],(sp)`
(length 2), then `add -4,sp` at `0x6edc1106` (length 3). This establishes
only the register-save and stack-allocation prologue, ending before
`0x6edc1109`. It does not identify a receiver or dispatch table, prove an
entry edge, or establish register preservation through later indirect calls.
No runtime readiness, capture, image production, or transfer follows from
this span.

### ThroughImage receiver and selector scalar

The constructor-shaped body at `0x6edfc227` (block-0 offset `0x007fae07`,
79 bytes) installs table `0x6eefbc84` through the incoming receiver, clears
fields, initializes embedded objects at `+12` and `+48`, and returns the
receiver. The existing authenticated table at offset `0x008fa864` selects
`0x6edfc346` through slot `+0x20`. That already-reviewed caller supplies
selector 4 to `0x6e868efe`, saves its scalar result, and forwards it in `d0`.
“ThroughImage” is a research label, not proof of a JPEG or frame owner.

The accepted selector span at `0x6e868efe` (offset `0x00267ade`,
56 bytes) maps selector 4 to `0x2100`, selector 5 to `0x2400`, and other
values to `0x0c00`. It passes a stack halfword destination to `0x6e76d553`,
clears that halfword when the helper reports nonzero status, then loads it
unsigned into `d0`. The separately accepted three-byte return at
`0x6e868f36` (block-0 offset `0x00267b16`) is `ret [d2],12`, completing
local coverage through `0x6e868f39` without changing the scalar interpretation.

The helper at `0x6e76d553` (offset `0x0016c133`, 224 bytes) searches
8-byte records from runtime `0x6034aff0`, compares halfword keys, and uses
`0x2900` as the sentinel. A matching record's word at `+4` is passed to
`0x6e76efc8` and `0x6e76ee46`; the latter also receives the saved destination.
The helper returns a halfword status. The three spans and 47 additional
instruction rows bound this static selector/scalar path. The runtime records,
concrete value selected for `0x2100`, downstream callee effects, and runtime
reachability remain unresolved. No image payload pointer, capture, transfer
queue submission, or wire completion is established.

The additional root-load rows at `0x6e76d58c` and `0x6e76d592`
explicitly establish the helper's `0x6034aff0` base. A separate 51-byte
initializer-shaped span at `0x6e76df43` (block-0 offset `0x0016cb23`)
passes `0x2100` and a reference to the authenticated `MENU_BG` identifier
(offset `0x0036c8bf`, 8 bytes) to `0x6e76edd1`. The accepted rows at
`0x6e76edd2` and `0x6e76edd8` load `0x6e96def4` and store it through
`a2`. These are static initialization facts; they do not identify the live
`0x2100` record's `+4` value or establish that this initializer populates
`0x6034aff0`. The six additional instruction rows and two ranges leave the
join to the queued-copy frontier at `0x6e61fd8d` / `0x6e68939a` unresolved.

The accepted 75-byte span at `0x6e76edd1..0x6e76ee1c` (block-0
`[0x0016d9b1,0x0016d9fc)`) adds 20 instruction rows around the existing
table installation. It saves incoming `a0` in `a2`, stores incoming `d0`
and `d1` at receiver offsets `+12` and `+16`, copies stack arguments into
fields `+20`, `+22`, `+24`, `+28`, and `+30`, and clears field `+4` before
the intervening call. The trailing `ret [d2,a2,a3],16` is now canonical.
The range also authenticates intervening instructions not individually recorded
in the corpus. This initializer-shaped coverage does not establish the caller's
argument identities, register preservation across the call, the live record's
producer, or a join to an image or transfer consumer.

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
- The current X3C source-vector span at block-0
  `[0x00d58918,0x00d58988)` is now authenticated in full: 112 bytes,
  or 28 four-byte entries. It shares its final 40 bytes with the previously
  authenticated range beginning at `0x00d58960` and ends where the adjacent
  vector at `0x00d58988` begins. The accepted indexed load at `0x6f333527`
  names runtime base `0x6f359d38`, distinct from `0x6f359da8` below.
  Source authentication alone does not establish runtime table placement,
  selection, ownership, or a live request path.
- A distinct dispatcher at `0x6f33362c` accepts selectors
  `0x5001..0x501c`, subtracts `0x5001`, scales the result by four, and indexes
  the target vector at runtime base `0x6f359da8`. The complete 28-word vector
  is authenticated at block-0 offset `0x00d58988`; slot 0 contains
  `0x6f334a8c`. The enclosing 38-word vector at `0x00d58960..0x00d589f7`
  is also authenticated and includes neighboring value `0x6f334aef`. The
  first target builds a stack descriptor and calls `0x6e61fd8d` at
  `0x6f334aab`; the sibling body sets `d0=2` at `0x6f334acf` and calls the
  same handoff at `0x6f334aef`. The vector relationship does not establish a
  common entry ABI. These are static selector and neighboring-target facts,
  not proof of the dispatcher's runtime owner, a live `0x5001` selection,
  ingress, serialization, or wire completion.
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
  through slot `+20` of an object reached from `d2+24`. The complete nine-byte
  helper at block-0 offset `0x0009d892` (local address `0x6e69d892`) reads
  an unsigned byte from `(d3,a3)` into `d0`, clears `d1` and `d0`, compares
  `a0` with 20, and returns. This bounded leaf does not identify the indirect
  callee or establish capture, image ownership, or transfer. Newly authenticated
  neighboring lookup families do not identify the consumer. Reviewed
  local-overlay routines select between four-byte-indexed bases `0x6e68ef1c`
  and `0x6e690a50` under global `0x8050`; other routines first consume distinct
  16- and 20-byte families around `0x6e690708` and `0x6e69081c`. Their geometry
  is incompatible with the 28-byte records, while the separate 34-word vector
  at block-0 offset `0x00090a98` still has no authenticated code reference. No
  runtime owner selects the 17-record table, so it does not add a `0x100e` arm
  to the primary selector or prove request admission.
- A caller-side branch at `0x6f32d597` reaches a status dispatcher at
  `0x6f32d9dc`. It reads record `+8` and branches on values 0 through 3:
  status 0 calls the descriptor builder at `0x6f32da0e`, status 1 calls the
  bounded routine at `0x6f32da3f..0x6f32daca`, status 2 reaches
  `0x6f32d9ff` and calls `0x6f32dacd`, and status 3 calls `0x6f32dae1`.
  The status-0 builder reaches `0x6e61fd8d`. Within the status-1 routine, four
  direct calls reach the complete leaf at `0x6f32db27`; it returns the
  unsigned halfword read from `0x60355a2c` in `d0` without writing `d2`.
  The same routine loads the pointer at `0xa07b702c` and calls it indirectly
  at `0x6f32dab1`. The setup sequence stores
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
  callers supply both fields for the same indices. Complete caller ranges are
  now authenticated at `0x6e68002c` (120 bytes), `0x6e680246` (98 bytes),
  `0x6e68042c` (114 bytes), and `0x6e6809b8` (97 bytes). Each saves incoming
  `a1` in `a2` and supplies it in `a0` to the paired writers; none establishes
  a concrete address for that incoming object. The second fields contain
  constants `0x1000`, `0x8000`, or zero, without an established executable
  handler identity. This geometry is compatible with the 16-slot table if
  the incoming base is `0x6f358d30`, but no accepted instruction establishes
  that alias or its runtime owner. This proves a
  candidate materializer shape, not table ownership, serialization, endpoint
  submission, DMA, or wire completion.
- Five bounded searches use 16 eight-byte slots: the initial search uses
  `[0x6f358d44,0x6f358dc4)`; subsequent status values 0, 1, 2, and 3 select
  banks beginning at `0x6f358cc4`, `0x6f358c44`, `0x6f358bc4`, and
  `0x6f358b44`, respectively. The status getter at `0x6f3311b2` reads the
  unsigned halfword at `0xa07b81a4`. Each search starts at the low four bits
  of the incremented record `+8` value, compares the full value at slot `+0`,
  wraps at the bank end, and jumps through matching slot `+4`; a zero key
  exits the search. In particular, status 2 reaches the search at
  `0x6f330b16` and indirect jump at `0x6f330b4d`. The four additional
  same-view source windows at block-0 offsets `0x00d58b44`, `0x00d58bc4`,
  `0x00d58c44`, and `0x00d58cc4` are now authenticated for 128 bytes each;
  their hashes do not establish runtime bank contents. No accepted producer
  establishes a slot containing callback landing `0x6f330b53`.
- The complete 123-byte body at `0x6f330ec2` preserves its incoming record
  pointer in `a2`. When byte `0xa07b81c8` is nonzero, it passes record fields
  `+0`, `+4`, and `+12`, with `d1=0xbb02`, to `0x6f33113f`, clears
  `0xa07b81b8`, and calls `0x6f331166` at `0x6f330f00`. That call saves
  `d2`; the helper's `ret [d2],8` restores the incoming value despite its
  internal `mov d0,d2`. The body then loads `0xa07b81a0` and invokes it at
  `0x6f330f0b`. The zero-guard branch instead copies 16 bytes from the record
  to `0xa07b81a8` and sets bytes `0xa07b82d7` and `0xa07b82d6` to one.
  The consumer at `0x6f3307f5` initializes `d2` to its post-prologue `sp+12`;
  its calls to `0x6f33093e` supply either fixed FIFO base `0xa07b81cc`
  (`0x6f330821`) or that local frame object (`0x6f330889`). The target arm
  at `0x6f330b53` forwards the selected record to `0x6f330ec2`. These are
  bounded object routes and a local callback register contract; the runtime
  table contents and selection of that arm remain unproved. They do not join
  this callback to the primary selector's descriptor output or establish a
  live operation handler.
- The complete containing initializer spans `0x6f32f6b5..0x6f32f864`; its
  suffix at `0x6f32f824..0x6f32f862` directly calls
  `0x6f3391d0` at `0x6f32f848` and `0x6f33c8f5` at `0x6f32f856`. The first
  path writes `0x6f33aa63` to `0xa07b702c` through setter `0x6f32d5f8`;
  the second writes `0x6f33e38f` to separate global `0xa07b7030` through
  `0x6f32d602` and installs `0x6f33e485` into `0xa07b81a0`. The reviewed
  `0x6f33e38f` entry fixes `d2` and its return value at 24, reaches helper
  `0x6e6050e5`, and returns through a 32-byte cleanup; the helper's nonzero
  `0x8050` path builds a size-128 descriptor and hands it to `0x6e61fd8d`.
  This differs from the record-populating shape of `0x6f33aa63`; at that
  installed entry, the unconditional branch at `0x6f33aaa6` skips the interior
  `0x6f33aaad` selector and its call to `0x6f33362c`. No accepted predecessor
  selects that interior entry, so adjacent registration does not join the
  installed callback to the `0x5001..0x501c` dispatcher or prove a shared
  callback signature. The last target
  `0x6f33e485` instead tests caller-supplied `d2`, conditionally reaches a
  diagnostic-looking helper, and returns `d2`. Canonical block-0 instruction
  rows contain no direct load of `0xa07b7030`; runtime ordering and ownership,
  the contract installed through `0xa07b702c`, and any indirect or runtime-built
  consumer of `0xa07b7030` remain unresolved. PTP namespace constants and local
  labels support a PTP-adjacent module attribution, but no RTOS task entry or
  operation-code ingress is established.
- A separate guarded setter at `0x6e6a9707` checks owner field `+0x1c`. When
  clear, it stores callback `a1` at `+0x3c`, context `d0` at `+0x48`, and
  returns the loaded zero guard; otherwise it returns `0x9a000201` (rendered as
  signed decimal `-1711275519`). Its paired consumer at `0x6e6a9720` returns
  without dispatch when `+0x3c` is null, or loads context `+0x48` and calls the
  stored target indirectly. Direct caller fragments at `0x6e6a0abe` and
  `0x6e6a224e` load the proposed callback and context from another object's
  fields `+172` and `+244` before reaching the setter. An authenticated caller
  beginning at `0x6e69ed55` forwards its incoming object into `0x6e6a0a58`;
  that path reads an owner candidate from object field `+288`, then obtains the
  callback and context from `+172` and `+244`. A related pair writes an incoming
  object to field `+288` at `0x6e6a0783` and later reads the field at
  `0x6e6a237c` before indirect dispatch through `0x6e6a224e`.
  The producer at `0x6e6a0742` now binds two incoming object roles: with
  `O` in `a0` and `S` in `a1`, its guarded path stores `O` at `S+0x30`
  (`0x6e6a077a`) and `S` at `O+0x120` (`0x6e6a0783`), then calls
  `0x6e6a224e`. Callback/context values come from `O+0xac` and `O+0xf4`.
  Thunks at `0x6e6ae092` and `0x6e6ae95e` load `O` from the pointer field
  at `parent+0x24` and call `0x6e6a0742` and `0x6e6a22c1`, respectively;
  `S` remains caller-supplied. Their authenticated block-0 spans are
  `(offset=0x000ae0b2, length=40)` and `(offset=0x000ae97e, length=40)`;
  the latter callee is covered by `(offset=0x000a22e1, length=214)`.
  New caller rows at `0x6e6caa8c` and `0x6e6d829e` directly reach
  `0x6e6ae092` after loading the source pointer through `a1`; the source
  class remains unidentified.
  An authenticated provider-aggregate construction span at block-0 offset
  `0x00653ab2` (222 bytes) constructs subobjects at `outer+0xe8` and
  `outer+0x1b0`. The setup spans at `0x00653f9d` (8 bytes) and
  `0x006540de` (15 bytes), with the setter at `0x00654fe6` (7 bytes),
  establish the local relation `O=outer+0x1b0`, `P=outer+0xe8`, and
  `*(O+0x128)=P`. The 184-byte constructor span at `0x00654340` clears
  `O+0x128` before later setup supplies that field.
  The exact factory frontier at `0x6e6a0a9d` loads `P=*(O+0x128)`, then
  calls the function pointer stored at `P+0x20`; there is no intervening
  load of a table from `*(P)`. That function pointer remains unresolved.
  These local object relations do not establish the concrete source class,
  writers of the callback/context values, a concrete callback routine,
  runtime ownership or ordering, or a join to the PTP selector, FIFO,
  ingress, USB, wire, or camera behavior.
- On the out-of-range-selector path, `0x6f33113f` uses record `+0` as a
  dynamic handle and constructs a 12-byte stack payload from the input
  halfword tag plus record fields `+4` and `+12`. It passes that payload
  through `0x6e61fd8d` to `0x6e68939a`, which copies it into dynamic queued or
  circular storage. Bytes 2 and 3 are not initialized by the builder. This
  proves a buffer-copy path, not USB/wire completion.
- Accepted coverage continues the storage corridor at `0x6e6893ae` through
  pointer walks rooted at table `0x8ff00004`. The current `0x8050` value makes
  one four-byte-indexed selection. A second index is derived as
  `(d0 & 0x7000) >> 12`; its selected owner's `+0x3c` field supplies a queue
  pointer, and queue `+0x1a` supplies an unsigned halfword bound. A source-only
  leaf at block-0
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

The caller window `0x6f331fb7..0x6f332029` (end exclusive), at block-0
offsets `0x00d31fd7..0x00d32049`, contains 47 contiguous instructions.
Full-width decoding corrects eight previously truncated lengths and slice
hashes without changing their instruction text or call targets. Five records
inside the call operands at `0x6f331ffd` and `0x6f33201b` were removed; no
independent alternate-entry evidence justifies retaining them. This correction
establishes static boundaries, not runtime reachability.

The owner-corridor loads at `0x6f331948`, `0x6f332c7f`, and `0x6f332d20`
are six-byte `mov (0xa07b87f0),a0` instructions. The former one-byte `a0`
records at `0x6f33194c`, `0x6f332c83`, and `0x6f332d24` lie inside their
operands and are removed without alternate-entry evidence. Calls at
`0x6f33195f`, `0x6f332112`, `0x6f33217d`, `0x6f332c99`, and `0x6f332d3d`
also have corrected full widths and slice hashes; instruction text and targets
are unchanged. These eight width corrections establish static boundaries only.

Full-width decoding at `0x6f331cf3` and ten starts within
`0x6f334b62..0x6f334c0b` establishes six-byte instructions. Eleven stale
four-byte rows and ten malformed one-byte `a0` operand fragments are removed;
nine correct full-width counterparts were already present. The overlapping
`jmp 0xde68afeb` at `0x6f331cf4` independently reproduces as five bytes, so
its length and slice hash are corrected while retaining the alternate decode.
An executable entry at that overlapping start remains unproven. These repairs
establish static widths only, with no new response or transfer claim.

The calls at `0x6f339800`, `0x6f339854`, and `0x6f33a8e0` (block-0
source offsets `0x00d39820`, `0x00d39874`, and `0x00d3a900`) have
complete lengths of seven, five, and five bytes respectively. These replace
three truncated four-byte records and their slice hashes; instruction text
and corpus counts are unchanged. The next instruction starts are
`0x6f339807`, `0x6f339859`, and `0x6f33a8e5`. These static width
corrections establish no runtime reachability or register preservation.

The `mov 1865784632,a1` at `0x6f333527` (block-0 source offset
`0x00d33547`) is six bytes, replacing its truncated four-byte record and
slice hash. The next instruction starts at `0x6f33352d`. This correction
establishes a static instruction boundary only; runtime reachability and
dispatch activation remain unproven. Corpus counts are unchanged.

The descriptor target's entry at `0x6e74c410` covers 21 bytes at block-0
offset `0x0014c430`. It tests the unsigned owner-relative halfword at `+138`
with mask `-8` and returns `0x7301` on the nonzero arm. Its zero arm now
continues into the reviewed dispatcher at `0x6e74c425..0x6e74c495`.
That span and operation bodies `0x6e74c631..0x6e74c67a` and
`0x6e74c67a..0x6e74c77b` add 188 full-width instructions over 442 bytes,
at block-0 offsets `0x0014c445`, `0x0014c651`, and `0x0014c69a`
respectively. All ends are exclusive; the return at `0x6e74c492` is three
bytes and ends at `0x6e74c495`.

The dispatcher distinguishes the descriptor's outer `+0` switch from its
nested `+2` switch. Outer `+0=1` with nested `+2=1` or `2` calls
`0x6e74c631` at `0x6e74c468`; outer `+0=2` instead calls `0x6e74c67a`
at `0x6e74c474`. On success it ORs the outer selector into the owner state
halfword. These are distinct operations: a later outer-2 invocation may
inherit state from an earlier outer-1 operation.

The first body copies owner fields `+4` and `+8` into `+24` and `+28`,
calls `0x6e8d9b7d`, and checks the halfword at owner `+96` for nested
selectors 1 and 2. The second body requires bit 0 in owner `+138` and
conditionally writes derived values to owner `+112`, `+116`, and `+120`,
with a result halfword at `+124`. Its paths depend on helper results and
preexisting owner state. These static field writes do not establish the
helpers' complete behavior, a selected runtime owner, image/file identity,
capture, USB/PTP submission, or wire completion. No immediate consumer of
the resulting owner fields is established by these spans.

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
