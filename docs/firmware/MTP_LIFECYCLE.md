# MTP lifecycle candidates and receive-record processing

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open questions](../RESEARCH.md)

Named start/end bodies, candidate aggregate relationships, and record-processing
calls provide static starting points for MTP research. Missing receiver and
selection connections prevent treating them as a proven live session path.
The [PTP record machinery](PTP.md) and [observed retrieval](../observations/USB_AND_MEDIA.md#retrieval)
remain separate findings unless a specific connection is established.

- [Named MTP communication lifecycle callers](#mtp-communication-lifecycle)
- [Range-only lifecycle aggregate and state-selector candidates](#mtp-lifecycle-owner)
  - [Aggregate construction and field links](#aggregate-construction-and-field-links)
  - [State selector and conditional start target](#state-selector-and-conditional-start-target)
- [Receive-record submission and pump join](#mtp-event-pump)
  - [Record formation and selected processing](#record-formation-and-selected-processing)

<a id="mtp-communication-lifecycle"></a>
## Named MTP communication lifecycle callers

Two source-selected bodies associated with the identifiers
`api_comm_Start_Communication_MTP` and `api_comm_End_Communication_MTP` call a
shared set of status, notification, and event-shaped helpers. Two separate
wrappers call those bodies before conditionally forwarding a current field
value. The names and direct calls establish a bounded static lifecycle family,
not live MTP-session entry, host request ingress, or a transport completion.

| Role | Local address | Block | Offset | Length |
|---|---:|---:|---|---:|
| Start-associated body | `0x6e858cab` | 0 | `0x00258ccb` | 100 |
| End-associated body | `0x6e858d0f` | 0 | `0x00258d2f` | 65 |
| Shared status writer candidate | `0x6e858e48` | 0 | `0x00258e68` | 23 |
| Mount-status-shaped helper | `0x6e85e919` | 0 | `0x0025e939` | 44 |
| Start identifier | DATA-local `0x6e9b0882` | 0 | `0x003af462` | 33 |
| End identifier | DATA-local `0x6e9b08a3` | 0 | `0x003af483` | 31 |
| End-calling wrapper | `0x6ee1819a` | 0 | `0x008181ba` | 31 |
| Start-calling wrapper | `0x6ee181b9` | 0 | `0x008181d9` | 32 |

The 100 canonical instructions completely cover the six code spans. Their
CODE-local view uses `source + 0x6e5fffe0`; the two identifier ranges use the
separate conditional DATA-local view `source + 0x6e601420`. Coherent pointer
arithmetic across those views does not establish runtime placement.

The start-associated body calls `0x6e861c92` with fixed scalar inputs, copies
its current result through `d1` and `d2`, and compares the zero-extended value
with 2. The less-than arm calls `0x6e8615eb` with `d0=33`; both arms then call
`0x6e861599` with `d0=33`. The end-associated body begins with that latter
call. Each body next calls the mount-status-shaped helper with `d0=1` for start
or `d0=0` for end, calls the [receive-record submission wrapper](#mtp-event-pump)
at `0x6e85ef16`, and calls the shared writer candidate with the same fixed
start/end scalar. Intervening opaque calls prevent binding later current
registers to earlier values unless the relevant preservation contract is
established.

The shared writer candidate copies incoming `d0` to `d2`, performs an opaque
reporting call, and writes current post-call `d2` as a halfword to
`0x605fc9d4`. This does not prove that the written value equals the incoming
start/end scalar. The mount-status-shaped helper retains incoming `d1` in its
stack record, selects current `d1=1` when current post-reporting low-byte `d2`
equals 1 and otherwise selects 7, loads a halfword through `0x6e691ad8`, and
calls `0x6e8605d5`. The called helper's effect and the numeric meanings remain
unresolved.

The wrappers call the end- or start-associated body and then inspect a current
pointer at current `a2+4` or `a2+8`; a nonzero value is forwarded to
`0x6edec994`. Although each wrapper initially copies incoming `a0` to `a2`,
preservation across the lifecycle call is not established, so the later field
cannot yet be assigned to the incoming object. No accepted edge establishes
that either wrapper is selected by a live MTP session, or connects the family
to shooting permission, capture, image ownership, USB submission, or host
completion.

**Next evidence:** [Live MTP selection](../RESEARCH.md#r-mtp-selection).

<a id="mtp-lifecycle-owner"></a>
## Range-only lifecycle aggregate and state-selector candidates

Authenticated construction, field-link, and indirect-dispatch spans connect a
large aggregate to the accessor and constructor around the MTP lifecycle
family. A separate state selector reaches a helper that loads receiver field
`+372` and calls virtual slot `+24`. This is range-only structural support:
none of these spans adds a canonical instruction row, and the missing receiver
and preservation join prevents treating the helper as a selection of the
aggregate's start wrapper.

| Role | Local address / placement | Block | Offset | Length |
|---|---:|---:|---|---:|
| Outer orchestration tail | `0x6ec83a30` | 0 | `0x00683a50` | 14 |
| Aggregate construction body | `0x6ec83af0` | 0 | `0x00683b10` | 123 |
| Aggregate field-link slice | `0x6ec83c03` | 0 | `0x00683c23` | 207 |
| Field-372 slot +8/+16 wrappers | `0x6ec84033` | 0 | `0x00684053` | 31 |
| Field-372 writer | `0x6ec843be` | 0 | `0x006843de` | 7 |
| Field-8-to-field-372 wrapper | `0x6ec84c90` | 0 | `0x00684cb0` | 14 |
| Field +8 writer | `0x6ec84da6` | 0 | `0x00684dc6` | 6 |
| Slot-24 helper initializer prefix | `0x6ec84102` | 0 | `0x00684122` | 11 |
| Field-372 / slot-24 helper | `0x6ec84236` | 0 | `0x00684256` | 20 |
| State selector's immediate caller | `0x6ec84778` | 0 | `0x00684798` | 69 |
| Field-412 state selector | `0x6ec848ea` | 0 | `0x0068490a` | 30 |
| State-6 writer | `0x6ec84910` | 0 | `0x00684930` | 13 |
| State-6 arm | `0x6ec8491d` | 0 | `0x0068493d` | 190 |
| State-7 writer | `0x6ec849e3` | 0 | `0x00684a03` | 13 |
| State-7 arm | `0x6ec849f0` | 0 | `0x00684a10` | 104 |
| Singleton-style accessor | `0x6ee17e23` | 0 | `0x00817e43` | 44 |
| 208-byte aggregate constructor | `0x6ee17ea7` | 0 | `0x00817ec7` | 134 |
| Separate Boolean-shaped leaf | `0x6ee180a8` | 0 | `0x008180c8` | 29 |
| Candidate adapter table | DATA-local `0x6eeacbb8` | 0 | `0x008ab798` | 124 |
| Nine-word target-shaped table | placement unresolved | 0 | `0x008fe678` | 36 |

The 18 code spans use the conditional CODE-local view
`source + 0x6e5fffe0`. The candidate adapter table uses the separate
conditional DATA-local view `source + 0x6e601420`; the 36-byte table remains
placement-unresolved. Both tables are data-shaped, not MN103 code. Coverage
authenticates each span but does not itself establish the contextual decodes
summarized below. In particular, the 207-byte field-link range ends inside the
final decoded call, so it is not a complete instruction listing or function
body.

### Aggregate construction and field links

The orchestration tail calls the field-link slice and then the construction
body with a shared current aggregate candidate. In the construction body, three
factory/accessor calls produce current pointer candidates. One is the
singleton-style accessor at `0x6ee17e23`. Calls to the field-372 writer place
the three current candidates through subobjects based at aggregate offsets
580, 112, and 1208; later calls and fixed scalars 1, 2, and 3 configure other
aggregate-relative subobjects. Opaque factory and setup calls leave returned
identity, preservation, validity, and lifetime unresolved.

The seven-byte writer stores incoming `a1` at receiver field `+372`. The two
wrappers at `0x6ec84033` and `0x6ec84041` load that current field, then call
its current table slot `+8` or `+16`. The separate `0x6ec84c90` wrapper loads
receiver field `+8` and reaches the slot-`+8` wrapper. The six-byte writer
stores incoming `a1` at receiver field `+8`. Within the field-link slice, one
complete direct call uses that writer to place aggregate-relative object
`+112` at field `+8` of aggregate-relative object `+536`. These are local
field and dispatch relations, not concrete class names or runtime method
selection.

The singleton-style accessor reads global pointer `0x6035b13c`. Its null arm
requests 208 bytes, conditionally calls the constructor at `0x6ee17ea7`, and
writes the current returned pointer back to the global before a shared tail.
The constructor initializes subobjects at offsets 0, 12, 24, and 36, then
eight 20-byte-spaced subobjects at offsets 48 through 188, calls a final helper,
and returns its saved aggregate pointer. This provides a bounded construction
shape near the start/end wrappers.

### State selector and conditional start target

The immediate caller passes its incoming `a0` unchanged to a selector.
That selector reads field `+412`, compares the current value with 7 and then 6,
and calls distinct state-7 or state-6 arms. Separate writers store 7 or 6 to
both fields `+408` and `+412`; no accepted owner assigns those values a host,
session, USB-personality, connected, or shooting meaning.

The state-7 arm can reach the field-372 / slot-24 helper, but only after two
direct calls with empty preservation masks and an indirect slot-`+8` call with
no preservation mask. The helper then loads field `+372` from its current
receiver, dereferences that object's table, and calls virtual slot `+24`.
Consequently, the current receiver at that call is not established as the
state-7 arm's entry receiver or the construction body's aggregate-relative
object `+112`. The state-6 sibling uses separate slot-`+8` behavior and does
not call the slot-24 helper.

Conditionally, if the helper receiver were the previously established
aggregate-relative object `+112`, its field `+372` would hold the
singleton-relative object `+12`, whose table slot `+24` maps to the named MTP
start wrapper at source `0x008181d9`. These spans do not establish that
receiver identity, so this remains a selector frontier rather than a selected
MTP-start dispatch. The candidate adapter table's slot `+68` maps only under
its separate DATA-local relation to the existing field-8-to-field-372 wrapper;
it is not a consumer of the helper's virtual slot `+24`.

The separate Boolean-shaped leaf calls `0x6e872e39` with `d0=0x02020400` and
returns 1 for a current zero result or 0 otherwise. Its caller and meaning are
unjoined. The nine-word table contains target-shaped values in the
`0x6ee194a5..0x6ee195f9` area, but no accepted consumer or placement joins it
to this aggregate.

The range-only construction, state selection, and field geometry nominate an
owner and selector frontier; they do not prove live allocation/order, MTP
mode, session ownership, wrapper selection, host ingress, shooting permission,
capture, image ownership, USB/wire submission, or completion.

**Next evidence:** [Live MTP selection](../RESEARCH.md#r-mtp-selection).

<a id="mtp-event-pump"></a>
## Receive-record submission and pump join

The start/end lifecycle bodies directly reach a small wrapper which calls a
larger receive-record submitter. That submitter builds a stack record, calls a
record-processing body, and on selected paths reaches two pump-shaped helpers.
This joins previously separate static stages inside one bounded family; it does
not establish the runtime task, live MTP selection, transport input, event
meaning, or delivery to USB.

| Role | Local address | Block | Offset | Length |
|---|---:|---:|---|---:|
| Lifecycle-called wrapper | `0x6e85ef16` | 0 | `0x0025ef36` | 13 |
| Receive-record submitter slice | `0x6e85f180` | 0 | `0x0025f1a0` | 224 |
| Record processor, first span | `0x6e86044e` | 0 | `0x0026046e` | 94 |
| Record processor, later span | `0x6e8604be` | 0 | `0x002604de` | 144 |

All four rows are authenticated ranges under the conditional CODE-local view
`source + 0x6e5fffe0`. The 183 canonical instructions fully cover the wrapper
and both record-processor spans. They cover 223 of the submitter slice's 224
bytes: source `0x0025f27f` is not a canonical instruction byte, so the slice is
not a complete body. The processor spans also leave source
`[0x002604cc,0x002604de)` outside this local-view submission. Existing rows in
that gap use a different local-address view; their bytes do not establish one
continuous `0x6e86...` execution view across the two spans.

### Record formation and selected processing

The wrapper copies incoming `d0` to `d2`, calls the submitter, and tests current
post-call `d2`. Its zero arm returns within the authenticated span; its nonzero
branch targets `0x6e85ef23`, outside the span. The submitter initializes stack
fields at `+12`, `+16`, `+20`, `+24`, `+28`, and `+32`, then calls the record
processor with `a0=sp+16`. A current unsigned value at `sp+28` greater than
zero selects the covered continuation; the other arm returns zero. The record
and branch geometry are established, but their field meanings and producer are
not.

In the selected continuation, the submitter tests the current word at `sp+40`
against `0x02000100`, `0x02000101`, `0x02010100`, and `0x02010101`, and
conditionally calls `0x6e85f10b`. It copies the current `sp+40/+44` pair to
`sp+48/+52`, calls `0x6e85f33e`, and can copy that pair to `sp+4/+8`. It then
calls `0x6e85fa20` with the unsigned halfword at `sp+36`, tests bit 1 of
`0x605fc9dc`, and on another covered arm calls `0x6e85fa4f` before a second
`0x6e85fa20` call and bit-1 test. Branches at `0x6e85f22a`, `0x6e85f238`,
and `0x6e85f258` leave the authenticated slice. The final covered path sets up
arguments at `0x6e85f25a..0x6e85f25e`, but the next instruction begins at the
unrecorded suffix; no final submission, retry, or return effect follows from
this slice.

The record processor reads pointer/value pairs through input fields `+0`, `+4`,
`+8`, and `+16`. Its first span treats current field `+4` values 0 and -1 as a
zero auxiliary scalar, compares field `+0` with halfwords reached through
`0x6e691bf2` and `0x6e691bf4`, and selects calls to `0x6e61fd33` or
`0x6e8606eb`. The later span reports current state and returns current `d3` as
-1, 0, or 1 on its covered paths; the zero path copies the current pointee of
the saved `+8` pointer to input field `+12`. Because the two spans are separated
by the address-view gap and reporting calls precede later tests, this does not
establish a complete processor contract or unconditional result mapping.

The direct calls establish a static submitter-to-processor-to-pump-shaped join.
Opaque effects, uncovered exits, record ownership, scheduling, retry behavior,
numeric meanings, and the writer or lifecycle of `0x605fc9dc` remain
unresolved. Nothing here establishes host request admission, shooting
permission, capture, image identity, USB/wire submission, or completion.

**Next evidence:** [MTP record owner and consumer](../RESEARCH.md#r-mtp-record-owner)
and [queued-storage research](../RESEARCH.md#r-ptp-storage).
