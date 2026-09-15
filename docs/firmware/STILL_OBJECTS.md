# Objects in the still research corridor

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

The evidence resolves a singleton dispatch and several distinct object/table
relationships. Their relationship to capture initiation or an image owner is
unresolved. Shared methods do not establish shared receiver identity.

- [Singleton dispatch and list population](#singleton)
- [Separate object at owner field +2216](#owner-2216)
- [Slots +72 and +76 and their continuations](#continuations)
- [Native still-request receiver boundary](#native-still-request)
- [Native still-take command boundary](#native-still-take)
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
Both spans have canonical instruction support. At source `0x0081be61`
(local `0x6ee1d281`), the two-byte `mov d3,a0` supplies the local record
address to the initializer.

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
| Conditional record table | 0 | `0x008feac4` | 20 |
| Record field +4 getter | 0 | `0x0081a396` | 6 |
| Record field +8 getter | 0 | `0x0081a3a2` | 6 |

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

Under the separately conditional DATA-local `source + 0x6e601420` view,
the installed record literal `0x6eeffee4` nominates source `0x008feac4`.
Its `+4` and `+12` words nominate the six-byte leaves at `0x0081a396`
and `0x0081a3a2`. The first reads current `P+4` into `d0`; the second
reads current `P+8` into `a0`, not `d0`. The latter's distinct recorded
load-address anchor is retained as explained [above](#owner-2216).
Relating these current-field reads to initialization requires unchanged
relevant storage through intervening methods. Neither leaf gives those
fields opcode, capture, or completion semantics.

These native input profiles are also nominated by the separately conditional
[E-table slots](RELEASE_CONTROL.md#conditional-receiver-endpoint), without
establishing shared object identity. Native `+64/+76` directly call
`0x0081c73b`, not endpoint `0x0081c0ec`; their direct calls do not test
global `0x6035b1ac`. Passing an equivalent record to that endpoint is a
hypothetical input contract, not an established native-producer call edge.
Stack validity during initialization and the call does not prove safe
retention after return, live table validity,
capture, image ownership, or completion.

The direct successor `0x6ee1db5b` (offset `0x0081c73b`, 103 bytes) also has
canonical coverage and is shared by the [conditional receiver-table
endpoint](RELEASE_CONTROL.md#conditional-receiver-endpoint). The source
coordinates below identify its replay without implying a global address view
or shared object/table identity.

Name the continuation's entering `a0/a1/d0` as `E/Q/P`. It saves `P` at
`sp+4`, `Q` in `d3`, and `E` in `a2`. The direct call at source
`0x0081c740` selects predicate `0x0081c3e1 [],0`. Its six canonical
instructions cover the complete 17-byte body through return `0x0081c3ef`:
it reads current `E+4` into `d1`, clears `d0`, and tests bit `0x20000`.
The `beq` at `0x0081c3eb` takes a clear bit directly to the zero return;
fallthrough sets `d0=1`. The body defines only `d0/d1`, with no calls or
data-memory writes, preserving entering `E/Q` in `a2/d3`.

The caller's `cmp 0,d0` / `beq` at `0x0081c745` / `0x0081c747`
takes that zero to `0x0081c758`. A set bit instead calls Q-table slot `+8`
at `0x0081c752` with `a0=Q,d0=-9`; that call's zero result at
`0x0081c754` / `0x0081c756` branches to the sole return at `0x0081c79f`.
Its unknown effects prevent extending the gate-clear preservation proof to
the gate-set arm.

Source `0x0081c758` clears `d2`, copies current `a2` to `a0`, and calls
that receiver's slot `+52` at source `0x0081c75f` (local `0x6ee1db7f`).
It saves current returned `a0` in `a3`. With an unspecified selected method,
this does not establish that `a2` still identifies the entering parent or that
`d2` remains zero.
Source `0x0081c762` compares **current** `d2,d3`, not unconditionally the
entering object against zero; equality branches to `0x0081c79e`. A separate
`cmp 0,a0` / `beq` at `0x0081c765` / `0x0081c767` takes null to that
same current-`d2` return-copy arm.

For the gate-clear arm, the separately conditional
[E-table slot +52](RELEASE_CONTROL.md#conditional-receiver-endpoint)
nominates the complete [field +100 getter](#field-100). That leaf writes only
`a0`, loading current `E+100`. Given valid entering objects and this selected
table, the early checks therefore have `a2=E,d3=Q,d2=0,a3=R`, where `R`
is that loaded pointer. `Q=0` or `R=0` takes the arm that copies zero to
`d0` and returns.
Otherwise the first unproved indirect effect is Q-table slot `+40` at
`0x0081c771`, with `a0=Q,a1=E`. Source `0x0081c76b` copies `a2` to
`a1`; `0x0081c76c` then loads Q's table into `a2`, and `0x0081c76e`
loads its `+40` target into that register. Thus `a2` is the method target
at the call; the E argument is in `a1`. This qualified join identifies
neither R's type nor an image owner.

For either arm, source `0x0081c773` then **loads** global `0x6035b1ac` into
`d0`, not a write of the slot's returned result. Source `0x0081c779` /
`0x0081c77a` compares that load with current `d2` and takes different to
`0x0081c78a`. Equal invokes current result-table slot `+8` with saved stack
`d0` and current `d3` as `a1`; different invokes saved-stack-pointer table
slot `+4` at `0x0081c791`, then current result-table slot `+48`. That
P-table call is distinct from the Q-table `+40` call. Neither path establishes
preservation of the entering objects or the slot-`+52` result across the
intervening indirect calls. Source `0x0081c79e` copies current `d2` to `d0`;
`ret [d2,d3,a2,a3],24` at `0x0081c79f` restores the caller's registers
separately from those internal identities and returns no identified payload.

**Unresolved:** the returned object's ownership and its connection to an image
consumer. The supported result is the dynamic-dispatch and return mechanics.

**Next evidence:** [Trace the pointer stored in field
+100](../RESEARCH.md#r-still-field-100).

<a id="native-still-request"></a>
## Native still-request receiver boundary

A native caller conditionally reaches a typed-argument construction and an
indirect receiver call associated with a still-request diagnostic. The source
relationship establishes argument formation and the first dynamic-effect
boundary, not request publication, capture, or a resulting image.

| Role | Block | Offset | Length | Support |
|---|---:|---|---:|---|
| Typed-argument constructor | 0 | `0x0059b994` | 21 | Canonical instructions |
| Conditional caller | 0 | `0x006a257e` | 78 | Canonical instructions |
| Native request body | 0 | `0x006a8ec3` | 96 | Canonical instructions, including one earlier row |
| Separate direct-call anchor | 0 | `0x007bddd9` | 7 | One canonical instruction |

The 68 canonical instructions use CODE-local view `source + 0x402c0000`.
The caller saves current `a0` in `a2`, reads field `+236`, and returns when
that value is nonzero. The zero arm crosses three direct helper calls before
restoring current `a2` to `a0` and calling source `0x006a8ec3`. Their listed
return masks preserve `a2`, but do not establish the receiver's lifetime,
the field meaning, or live entry into this caller. The separate instruction at
source `0x007bddd9` also directly calls the same body without establishing its
own caller contract.

The request body first supplies a stack word containing 1 to a predicate call.
A current zero result returns immediately. On the other arm it requests 28
bytes; a non-null current return reaches the constructor, which calls a base
helper and then writes table literal `0x6ee4f9b0` and halfword 26817 through
current post-helper `a0`. This does not prove that the writes target the
allocation result or identify a persistent request object.

The body then initializes a stack record and reaches an indirect call through
the current field-`+140` receiver's table slot `+4`, with the current
constructor candidate in `a1`. A diagnostic associated with sending
`evTraResShtStartShootingPicture` occurs only **after** that call. The string
and ordering do not identify the selected method or prove that the request was
published. Current receiver, candidate, stack-record, and register identities
depend on intervening opaque calls; matched masks at outer returns do not prove
their internal preservation.

The dynamic slot's concrete owner and effect, live inbound selection, exposure,
new-image identity, and host retrieval remain unresolved. The body is not a
safe patch or host-control interface merely because it constructs a typed
argument and reaches a named diagnostic.

**Next evidence:** [Resolve the release-control and native request
consumers](../RESEARCH.md#r-release-contract).

<a id="native-still-take"></a>
## Native still-take command boundary

A dispatch arm forwards its current `d2` value to a bounded native still-take
body. The callee saves that input immediately, and a source label identifies a
still-take phase. These facts establish a direct scalar handoff and a useful
effect frontier, not shutter actuation or a completed capture.

| Role | Block | Offset | Length |
|---|---:|---|---:|
| Caller argument and direct call | 0 | `0x00220236` | 6 |
| Separate enclosing return anchor | 0 | `0x00220365` | 3 |
| Complete authenticated callee span | 0 | `0x00220368` | 935 |
| Still-take diagnostic identifier | 0 | `0x0039d7fd` | 17 |

The code rows use local view `source + 0x402c0000`. At source `0x00220236`,
`mov d2,d0` is immediately followed by the direct call to source
`0x00220368`; the callee's first canonical instruction stores entering `d0`
at `sp+28`. This proves the local input handoff. The return instruction at
source `0x00220365` is separately canonical, but the gap after the call is not
a complete canonical control-flow listing and does not establish the returned
status or caller outcome.

The 935-byte range authenticates the callee through its complete return at
source `0x0022070c`, while only six interior instructions are canonical. A
selected test at `0x002204f8` compares current `d1` with zero and branches
nonzero to `0x00220547`. On the zero fallthrough, range-only context associates
the separately authenticated `Still Take Start` identifier before later
selected anchors at `0x00220509` and `0x0022053d`. Those anchors load current
field `a3+32` and call `0x404d7980`, respectively, but the intervening bytes
are not a canonical instruction listing and do not establish preserved
arguments or the callee's effect.

The complete authenticated extent and diagnostic name do not prove that the
body is entered live, that its scalar denotes a host request, or that any
sensor exposure, file creation, new-image ownership, transfer, or completion
occurs. Establish those effects at a bounded selected call before treating the
body as a controllable capture interface.

**Next evidence:** [Resolve the release-control and native request
consumers](../RESEARCH.md#r-release-contract).

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
