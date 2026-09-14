# Objects in the still research corridor

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

The evidence resolves a singleton dispatch and several distinct object/table
relationships. Their relationship to capture initiation or an image owner is
unresolved. Shared methods do not establish shared receiver identity.

- [Singleton dispatch and list population](#singleton)
- [Separate object at owner field +2216](#owner-2216)
- [Slots +72 and +76 and their continuations](#continuations)
- [Field +100 getter and writer](#field-100)

<a id="singleton"></a>
## Singleton dispatch and list population

An instruction anchor for this research area is `mov a0,a3` at `0x4096368d`
(block 0, offset `0x006a36ad`, length 1).

The indirect calls at `0x40963771` and `0x409637d1` both load slot `+4` from
the table of the singleton stored at runtime global `0x60358c3c`. Its
constructor installs table address `0x6ee69030`. All eight table slots and the
corresponding target source spans have authenticated coverage; slot `+4`
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

The singleton lifecycle includes construction, dispatch, and cleanup. Its
getter, constructor, destructor body, and cleanup reset all have authenticated
spans; the cleanup path loads and clears global `0x60358c3c`, and the
constructor/destructor evidence uses the same table value `0x6ee69030`.
Direct-call and literal censuses do not exclude indirect writes or prove that
every candidate use is reachable.

**Next evidence:** [Identify the still-corridor list
consumer](../RESEARCH.md#r-still-list).

<a id="owner-2216"></a>
## Separate object at owner field +2216

A separate object path stores its incoming pointer at owner-relative field
`+2216`, calls slot `+0` through that pointer, reloads the same object, and
calls slot `+8` at `0x409613d8`. Its lazy constructor installs table
`0x6ee8d1d0`; slots `+0`, `+4`, and `+8` resolve to `0x6ec1875c`,
`0x6ee1d507`, and `0x6ee1d553`. The slot-`+8` body performs a guarded
one-time initialization of three words at `0x6065949c` through `0x6ee1b784`,
then calls the same object's slot `+4` at `0x6ee1d583`. The slot-`+4` body
reaches several further receiver-relative indirect calls, beginning at
`0x6ee1d52a`. These object, table, and target identities differ from the
established singleton above; the concrete runtime receivers, semantic class,
and any downstream relationship to the still corridor remain unresolved.

The nested call at `0x6ee1d52a` loads receiver-table slot `+12`. The canonical
six-byte range at block-0 offset `0x0081a3a2`, decoded locally at `0x6ee1b7c2`, is `mov (8,a0),a0` followed by `retf [],0` at `0x6ee1b7c5`. The return is
canonical. The load row retains address `0x6ee1b7c8` for that source offset; no
load row at the alternate local address is admitted. Under the local view, the
bounded body is a field getter.

**Unresolved:** the field meaning, receiver identity, and downstream image
ownership.

**Next evidence:** [Identify the nested receiver of the +2216
object](../RESEARCH.md#r-still-receiver).

<a id="continuations"></a>
## Slots +72 and +76 and their continuations

These slots lead to helper calls and further receiver dispatch. Slot `+76` is
called at `0x6ee1d53a` when the earlier getter result is nonzero.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Slot +72 | `0x6ee1d38f` | 0 | `0x0081bf6f` | 15 |
| Slot +64 | `0x6ee1d263` | 0 | `0x0081be43` | 57 |
| Slot +76 | `0x6ee1d39e` | 0 | `0x0081bf7e` | 45 |
| Direct successor | `0x6ee1db5b` | 0 | `0x0081c73b` | 103 |

For the established table `0x6ee8d1d0`, slot `+72` resolves to `0x6ee1d38f`
(block-0 offset `0x0081bf6f`, 15 bytes). Before any intervening call, it loads
`*(a0)`, selects that receiver table's slot `+64` at source `0x0081bf76`,
and calls it at `0x0081bf79` with unchanged entering `a0/a1/d0`. It forms no
local record and returns `ret [a2],8` at `0x0081bf7b`. Under the same table
identity, slot `+64` resolves to `0x6ee1d263` (offset `0x0081be43`, 57 bytes).
Both spans have canonical instruction support; the two-byte boundary at
`0x6ee1d281` has range coverage only. A source-anchored replay does not add an
instruction row at that boundary.

Name this native profile's entering `a0/a1/d0` as `E/Q/B`, without implying
recovered types. Slot `+64` saves `E` in `a2` and `Q` in `a3`.
Source `0x0081be4a` compares `0,d0`; `beq` at `0x0081be4c` takes `B=0` to
`0x0081be5c`. That arm forms `P=sp+4` in `d3`, initializes the local record
with field `+4=0`, restores `E/Q` from saved `a2/a3`, and supplies `P` in
`d0` to source `0x0081c73b` at `0x0081be6b`. Nonzero instead supplies
literal `0x60659490` in `d0` at `0x0081be4e` and directly calls the same
continuation at `0x0081be54`, without a prior call or overwrite of entering
`a0/a1`. That literal is not a source offset or an identified live owner.
Both arms save returned `d0` in `d2`; only the local-record arm resets `P`.
Source `0x0081be78` copies saved `d2` to `d0` before the 32-byte-frame return.

**Unresolved:** the runtime dispatch and
whether this scalar-returning continuation has any image-producing effect.

The adjacent slot `+76` maps to `0x6ee1d39e` (block-0 offset `0x0081bf7e`, 45
bytes). It saves entering `Q` at `sp+4`, `E` in `a3`, and copies entering
`B=d0` to `d1` at source `0x0081bf86`. It forms `P=sp+8` in `a2` and clears
`d0`. The compare `d0,d1` at `0x0081bf8c` / `beq` at `0x0081bf8d` takes
`B=0` to initializer call `0x0081bf91`; nonzero falls through to
`mov 1,d0` at `0x0081bf8f`. Thus the initializer receives `(B != 0)`, not
an unchanged scalar or an independently entering `d1` argument. With saved
`a2/a3` preserved by the complete local initializer, it reloads `Q`, restores
`E`, and passes `P` in `d0` to `0x0081c73b [d2,d3,a2,a3],24` at
`0x0081bf9b`. It saves returned `d0` in `d2`, resets the local record, copies
saved `d2` to `d0`, and returns `ret [d2,a2,a3],32` at `0x0081bfa8`.

| Local record support | Block | Offset | Length |
|---|---:|---|---:|
| Complete initializer | 0 | `0x0081a375` | 17 |
| Reset pre-return prefix | 0 | `0x0081a386` | 13 |
| Reset return | 0 | `0x0081a393` | 3 |

The complete initializer (`0x6ee1b795` in this local view) spans
`[0x0081a375,0x0081a386)`, including `retf [],0` at `0x0081a383`.
It writes `P+0=0x6eeffee4`, `P+4=entering d0`, and `P+8=0`; it has no calls
or writes to `a2/a3/d3`, supporting the native wrappers' pre-call argument
restoration. The 14-byte range at the same start is only its pre-return
prefix. The complete reset (`0x6ee1b7a6`) spans
`[0x0081a386,0x0081a396)`: it writes current `P+0` and `P+8`, clears `a0`,
and includes the return at `0x0081a393`. It does not write `P+4` or saved
result `d2`. These extents are assembled from the stated canonical context,
not evidence corrections. The continuation's listed return mask restores
the wrappers' saved record-address registers; the local reset does not
change their saved scalar result.

These native input profiles are also nominated by the separately conditional
[E-table slots](RELEASE_CONTROL.md#conditional-receiver-endpoint), without
establishing shared object identity. Stack validity during initialization and
the call does not prove safe retention after return, live table validity,
capture, image ownership, or completion.

The direct successor `0x6ee1db5b` (offset `0x0081c73b`, 103 bytes) also has
canonical coverage and is shared by the [conditional receiver-table
endpoint](RELEASE_CONTROL.md#conditional-receiver-endpoint). The source
coordinates below identify its replay without implying a global address view
or shared object/table identity.

It saves entering `d0` at `sp+4`, entering `a1` in `d3`, and entering `a0`
in `a2`. The direct predicate call at source `0x0081c740` selects
`0x0081c3e1 [],0`. Its `cmp 0,d0` / `beq` at `0x0081c745` /
`0x0081c747` skips the optional current-object table-`+8` call on zero,
branching to `0x0081c758`. On nonzero it calls that slot with `d0=-9`;
that call's own zero result at `0x0081c754` / `0x0081c756` branches to the
sole return at `0x0081c79f`.

Source `0x0081c758` clears `d2`, copies current `a2` to `a0`, and calls
that receiver's slot `+52` at source `0x0081c75f` (local `0x6ee1db7f`).
It saves current returned `a0` in `a3`. The unmasked calls do not establish
that `a2` still identifies the entering parent, or that `d2` remains zero.
Source `0x0081c762` compares **current** `d2,d3`, not unconditionally the
entering object against zero; equality branches to `0x0081c79e`. A separate
`cmp 0,a0` / `beq` at `0x0081c765` / `0x0081c767` takes null to that
same current-`d2` return-copy arm.

Otherwise it calls the current other object's table slot `+40` with current
`a2` as `a1`. Source `0x0081c773` then **loads** global `0x6035b1ac` into
`d0`, not a write of the slot's returned result. Source `0x0081c779` /
`0x0081c77a` compares that load with current `d2` and takes different to
`0x0081c78a`. Equal invokes current result-table slot `+8` with saved stack
`d0` and current `d3` as `a1`; different invokes saved-stack-pointer table
slot `+4`, then current result-table slot `+48`. Neither path establishes
preservation of the entering objects or the slot-`+52` result across the
intervening indirect calls. Source `0x0081c79e` copies current `d2` to `d0`;
`ret [d2,d3,a2,a3],24` at `0x0081c79f` restores the caller's registers
separately from those internal identities and returns no identified payload.

**Unresolved:** the returned object's ownership and its connection to an image
consumer. The supported result is the dynamic-dispatch and return mechanics.

**Next evidence:** [Trace the pointer stored in field
+100](../RESEARCH.md#r-still-field-100).

<a id="field-100"></a>
## Field +100 getter and writer

A getter and writer expose an object pointer field. The pointer's producer and
concrete receiver remain unresolved; a second table shares some methods.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Getter | `0x6ee1dc28` | 0 | `0x0081c808` | 6 |
| Writer | `0x6ee1d588` | 0 | `0x0081c168` | 9 |
| First table slot +40 | `0x6ee1d727` | 0 | `0x0081c307` | 3 |
| Separate initializer | `0x6ec0b717` | 0 | `0x0060b2f7` | 26 |
| Separate table candidate | `0x6ee8a59c` | 0 | `0x0088a17c` | 160 |

For parent table `0x6ee8d1d0`, slot `+52` resolves to the canonical six-byte
getter at `0x6ee1dc28` (block-0 offset `0x0081c808`): it loads field `+100`
into `a0` and returns. The accepted writer at `0x6ee1d588` (offset `0x0081c168`, nine bytes) stores incoming `a1` into fields `+100` and `+92`, then returns.
This identifies a setter body, not the producer or concrete dispatch table of
the stored object. The same parent table's slot `+40` resolves to `0x6ee1d727`
(offset `0x0081c307`, three bytes), whose accepted body is only `retf [],0`.
That bounded no-op does not identify the other incoming object's slot-`+40`
target at `0x6ee1db91`. The field value, its runtime provenance, and its later
slot-`+8`/`+48` consumers remain unresolved; none of these bodies establishes
image ownership or transfer.

The accepted 26-byte initializer at local address `0x6ec0b717` (block-0 offset
`0x0060b2f7`) clears `d0`, sets `a1` to zero, calls `0x6ee1a0ef`, then
writes table value `0x6ee8a59c` through the post-call `a0` and stores halfword
`2204` at `a0+4` before returning. The 160-byte table span at offset
`0x0088a17c` maps to `0x6ee8a59c` under the same local delta `0x6e600420`. Its
slots `+52` and `+56` contain the field-`+100` getter `0x6ee1dc28` and writer
`0x6ee1d588`; slots `+8`, `+64`, `+72`, and `+76` also share the previously
mapped targets. Its slot `+40`, however, contains `0x6edeeaf7`, so the no-op
established for table `0x6ee8d1d0` cannot be transferred to this table. These
source spans establish a separate table candidate with shared methods. They do
not prove the allocator/helper's behavior, the field-`+100` value's provenance,
or the runtime receiver at a later indirect call. The local address relation is
not a global load base.

**Next evidence:** [Trace the pointer stored in field
+100](../RESEARCH.md#r-still-field-100).
