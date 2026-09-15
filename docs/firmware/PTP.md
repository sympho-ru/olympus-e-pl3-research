# PTP-adjacent records, dispatch, and storage

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

This area contains request-shaped records, selector dispatch, callback
registration, and buffer operations. PTP namespace constants and local labels
support the area name; an RTOS task entry or host operation-code ingress is not
established. The sections below describe separate bounded relationships. Their
grouping is not proof that they form one request-to-host path.

Separate [USB observations](../observations/USB_AND_MEDIA.md) establish working
existing-image retrieval, while [handler experiments](../observations/DEPLOYMENT.md#advertisement)
show that the tested advertisement and static-route changes did not activate
the intended operations. Those measurements constrain the research without
identifying the routines below as their live implementation.

- [Named USB-state reporting wrapper](#usb-state-wrapper)
- [Candidate connection callback, byte stores, and consumer](#usb-connect-stores)
- [PC/USB state-transition policy and callers](#pc-usb-transition)
- [Named MTP communication lifecycle callers](#mtp-communication-lifecycle)
- [Range-only lifecycle aggregate and state-selector candidates](#mtp-lifecycle-owner)
- [Receive-record submission and pump join](#mtp-event-pump)
- [Registration callers and unresolved callback placement](#registration)
- [Record initialization and FIFO layout](#fifo)
- [Primary request selector and caller](#request-selector)
- [Neighboring source vectors and the 0x5001 selector](#selector-vectors)
- [Status dispatcher and installed callbacks](#status-callbacks)
- [Adjacent submitted-record consumer candidate](#submitted-record-consumer)
- [FIFO handler banks and candidate writers](#handler-banks)
- [Record route through the callback body](#callback-body)
- [Reply packing, queued storage, and buffer pool](#reply-storage)
- [Descriptor operations and owner-state fields](#descriptor-owner)
- [Separate callback object family](#callback-objects)
- [Unjoined descriptor tables](#descriptor-tables)
- [Handler boundary and unselected alternate starts](#unselected-entries)
- [Current instruction boundaries and alternate decode](#decode-boundaries)

<a id="usb-state-wrapper"></a>
## Named USB-state reporting wrapper

The source-selected body associated with `getUsbState` reports labels for two
current-register values and clears `d0` before normal return. Its name does not
establish a caller-visible numeric USB-state getter or a live connection state.

| Role | Block | Offset | Length |
|---|---:|---|---:|
| Source-selected wrapper | 0 | `0x005de67b` | 76 |
| Method name | 0 | `0x0086bb10` | 12 |
| Three-word row | 0 | `0x0086e5c0` | 12 |
| Zero-branch label | 0 | `0x008722ce` | 14 |
| One-branch label | 0 | `0x008722dc` | 17 |

The row contains pointer literals `0x6ee6cf30`, `0x6ebdfa9b`, and
`0x6ee6cf3c`. Under the conditional DATA-local view `source + 0x6e601420`,
the first selects the name and the second selects the wrapper. This coherent
view is not runtime placement or a universal code/data mapping; the third
word's role is unresolved. The two branch labels are `API_CONNECTED` and
`API_DISCONENCTED` (source spelling). They do not establish an enum domain or
actual USB personality, session ownership, or connection.

The wrapper's 21 canonical instructions use local view
`0x6ebdfa9b..0x6ebdfae7`. They leave a two-byte gap at source `0x005de68c`;
the 76-byte authenticated range is not a complete canonical instruction listing.
Source `0x005de680` calls local `0x6eb82317`, then loads `(a0)` into `a1`
and slot `+40` into `a1`. After the gap, source `0x005de68e` copies current
`d0` into `d2`. Binding this value to a live slot-40 result requires the
unresolved receiver, table, call, and method contracts.

Source `0x005de68f` defines `d0=65801` before the call at `0x005de695`
to local `0x6eb97e18,[d2],4`. Source `0x005de69c` copies current `d2`
into `d0` before `0x005de69d` calls `0x6eb80db8,[d2,a2,a3],28`.
The encoded masks alone do not prove either reporting callee's saved-stack,
return, or register-preservation contract. The later comparisons therefore
refer to current `d2`, conditionally related to the earlier copied value.

At `0x005de6a4`, `cmp 0,d2` and the following `beq` take zero to
`0x005de6ae`, which selects pointer `0x6ee737ee` for `API_CONNECTED`.
Otherwise `cmp 1,d2` at `0x005de6a8` and its `beq` take one to
`0x005de6b6`, selecting `0x6ee737fc` for `API_DISCONENCTED`.
Both selections join the reporting call at `0x005de6bc` to
`0x6eb80d74,[a2,a3],20`; other current `d2` values branch directly to
`0x005de6c3`. All normal paths through this selected body join `clr d0`
at `0x005de6c3` and the complete `ret [d2],8` at `0x005de6c4`.

Live receiver/slot ownership, value production, lifetime, synchronization, and
the reporting preservation contracts remain unjoined. This does not identify
shooting restrictions, capture initiation, image association, or host transfer.
See [USB/shooting-state research](../RESEARCH.md#r-usb-shooting-state) and the
separate [historical session observations](../observations/USB_AND_MEDIA.md#personalities).

<a id="usb-connect-stores"></a>
## Candidate connection callback, byte stores, and consumer

The candidate body at source `0x00acfa9b` selects two sets of explicit
one-byte writes through four direct-call leaves. It is not merely a reporting
wrapper. Its proposed USB-connect role does not establish live registration,
the meaning of the numeric states, or a shooting-state consumer.

The 78 canonical instructions completely cover block-0 source body
`[0x00acfa9b,0x00acfb69)` (206 bytes) and four nine-byte leaves at
`0x00acf958`, `0x00acf96a`, `0x00acf97c`, and `0x00acfa89`.
These are instruction coordinates, not canonical range rows. Their CODE-local
view is `source + 0x6e5fffe0`: body entry `0x6f0cfa7b` and leaves
`0x6f0cf938`, `0x6f0cf94a`, `0x6f0cf95c`, and `0x6f0cfa69`.
This local arithmetic does not prove runtime placement or a DATA mapping.

Entry copies are source `0x00acfaa0:d1->d2`, `0x00acfaa1:d0->d3`, and
`0x00acfaa2:a1->a2`. Initialization at `0x00acfaab` and reporting at
`0x00acfac5` intervene before the comparisons. Their encoded call masks do not
establish original-input preservation or a callback ABI; conditions below
refer to current `d3` and `d2` at the tests.

Source `0x00acfacc` compares `16,d3`; `beq` at `0x00acface` selects
`0x00acfad3`, while fallthrough returns at `0x00acfad0`. The selected chain
compares current `d2` with 3, 72, 71, and 70 at `0x00acfad3`,
`0x00acfad7`, `0x00acfadb`, and `0x00acfadf`. Taken branches at
`0x00acfad5`, `0x00acfad9`, `0x00acfadd`, and `0x00acfae1` select
the corresponding arms; an unmatched value returns at `0x00acfae3`.

| Current test values | Selected arm | Explicit byte writes, in order | Return |
|---|---|---|---|
| `d3==16`, `d2==3` | `0x00acfae6`; opaque call at `0x00acfaed` | None in the selected caller arm | `0x00acfaf4` |
| `d3==16`, `d2==72` | `0x00acfaf7`; opaque call at `0x00acfb03` precedes stores | `0x60353190=1`, `0x60353191=4`, `0x60353192=0` | `0x00acfb66` |
| `d3==16`, `d2==71` or `70` | `0x00acfb39` | `0x60353193=5`, `0x60353190=11`, `0x60353191=2` | `0x00acfb66` |

Each store argument is immediately defined in `d0` before its direct call:
sources `0x00acfb0a/0c`, `0x00acfb11/13`, `0x00acfb18/19`,
`0x00acfb39/3b`, `0x00acfb40/42`, and `0x00acfb47/49`.
The leaves contain complete six-byte `movbu d0,(address)` followed by
three-byte `retf [],0`. The two store arms perform further opaque calls;
the 72 arm branches from `0x00acfb37` to the shared return. All four return
sites have identical complete three-byte `ret [d2,d3,a2,a3],44`; not every
path reaches the final site.

These writes are conditional normal-execution effects, not proof of persistent
global values. Opaque helper effects, address validity, lifetime, and later or
concurrent changes remain unresolved; no-store arms do not prove unchanged
state. There is no established join to the named wrapper's slot-40 value.

A separate dispatcher and consumer read the same candidate-state storage. The
151 canonical instructions completely cover dispatcher
`[0x00acf65e,0x00acf691)`, consumer `[0x00acf74a,0x00acf83e)`, helper
`[0x00acf86b,0x00acf8b1)`, and getter `[0x00acf985,0x00acf98e)` under the
same conditional CODE-local `source + 0x6e5fffe0` view. The dispatcher calls
the consumer at source `0x00acf67b` when its current `d0` equals 4. This is a
source-level selection, not proof that the dispatcher is entered or that 4
denotes a live USB state.

The consumer initializes stack bytes `sp+4=1` and `sp+5=4`, calls the getter,
saves its returned `d0` in `d2`, and calls the 1,580-byte-frame helper. The
getter directly loads unsigned byte `0x60353192` and returns. Subsequent tests
use current post-helper `d2` and the low halfword of current `d0`; the encoded
call/return masks do not prove that they preserve the pre-helper values.

| Current post-helper values | Explicit branch-local effects before the shared tail |
|---|---|
| `d2=0`, `d0=0/1/2` | Call arguments `(d0,d1)=(14,13)`, `(14,14)`, or `(14,15)` to `0x6f09ad39` |
| `d2=0`, `d0=3` | Two opaque calls precede a current-`d0==1` split; equality selects another opaque call and a call with `d0=11`, while inequality selects `(14,17)` for `0x6f09ad39` |
| `d2=1`, `d0=0` | Store 36 through the existing `0x60353193` leaf, write stack bytes 0/2, then select `(14,17)` |
| `d2=1`, `d0=1` | Write stack bytes 0/0, store 2 through the `0x60353192` leaf, then call `0x6f0cf3fe` with `d0=2` and current saved consumer object in `a0` |
| `d2=2`, `d0=0` | Write stack bytes 0/0, then call `0x6f0cf96e` with pointers to those two stack bytes |
| `d2=2`, `d0=1` | Write stack bytes 0/0, store 3 through the `0x60353192` leaf, then call `0x6f0cf3fe` with `d0=3` and current saved consumer object in `a0` |

All other tested values reach the shared tail without those listed
branch-local effects. The tail reloads the **current** stack bytes and calls
the existing setters for `0x60353190` and `0x60353191`; intervening opaque
calls can change those bytes, globals, and receiver registers. In the helper,
the byte-derived `d3` calculation occurs before an opaque initializer call, so
the later table-address calculation uses current post-call `d3`. Its scratch
storage, table validity, loop termination, returned scalar, and preservation
effects remain unresolved.

The numeric states, calls, and byte stores do not identify connected versus
disconnected, Storage/MTP, shooting permission, capture, image ownership, host
transfer, or a safe mode override. They also do not connect this consumer to
the named wrapper's slot-40 value.

**Next evidence:** [USB/shooting-state research](../RESEARCH.md#r-usb-shooting-state).

<a id="pc-usb-transition"></a>
## PC/USB state-transition policy and callers

A range-only state family connects a 23-by-23 transition matrix, diagnostic
state names, record construction, and several PC/USB-labelled bodies. It
establishes an internal transition policy and bounded direct-caller edges, but
does not establish that a physical USB event selects them or that an accepted
transition changes the active interface or shooting availability.

| Role | Local address / placement | Block | Offset | Length |
|---|---:|---:|---|---:|
| Diagnostic state mapper | `0x6efcbd07` | 0 | `0x009cbd27` | 392 |
| Eight PC/USB-labelled bodies | `0x6efd3e99` | 0 | `0x009d3eb9` | 546 |
| Separate state-21 caller | `0x6efd41b0` | 0 | `0x009d41d0` | 71 |
| Disconnect-labelled conditional caller | `0x6efd4245` | 0 | `0x009d4265` | 90 |
| 23-by-23 transition matrix | DATA-local `0x6f10fd84` | 0 | `0x00b0e964` | 529 |
| State-name sequence | DATA-local `0x6f11004c` | 0 | `0x00b0ec2c` | 611 |

The four code spans use the conditional CODE-local view
`source + 0x6e5fffe0`; the matrix and names use the separate conditional
DATA-local view `source + 0x6e601420`. These are authenticated range anchors,
not canonical instruction rows. Contextual GNU MN103 decoding with source
lookahead supports the relationships below, but neither address arithmetic nor
the labels establish runtime placement or physical USB meaning.

The neighboring request owner preserves its proposed state in `d3` and its
receiver in `a2` across a validator call whose encoded mask includes both
registers. Only current validator result 1 selects the record mapper and the
store of the proposed state to `0x6034cf84`; the owner itself is contextual
source, not one of the canonical ranges above. The validator treats the
matrix row as proposed state minus one and the column as current state minus
one. Matrix values 0 reject, 1 are ordinary candidates, 2 conditionally call
virtual slot `+40`, and 3 conditionally call virtual slot `+48`; those calls'
zero-result tests make values 2 and 3 conditional rather than unconditional
transition effects.

The selected matrix cells for states 11, 17, 18, 19, 20, and 21 are:

| Proposed \ current | 11 | 17 | 18 | 19 | 20 | 21 |
|---:|---:|---:|---:|---:|---:|---:|
| 11 | 1 | 3 | 2 | 2 | 2 | 2 |
| 17 | 0 | 1 | 2 | 2 | 2 | 2 |
| 18 | 0 | 0 | 1 | 1 | 1 | 1 |
| 19 | 0 | 0 | 1 | 1 | 1 | 1 |
| 20 | 0 | 0 | 1 | 1 | 1 | 1 |
| 21 | 0 | 0 | 1 | 1 | 1 | 1 |

The state-name sequence labels 11 `CAM_SHOOTING`, 17
`PC_START_PC_USB_SELECT`, 19 `PC_START_PC_WAIT_USB_DISCONNECT`, 20
`PC_RETURN`, and 21 `PC_CAM_SHOOTING`. The record mapper associates state 19
with fields `+4=243` and `+20=277`. These labels and numeric fields describe
the internal records; they do not prove a USB event, state lifetime, or effect.

The eight-body span contains bodies associated by nearby name pointers with
USB selection, PC mode, PC start/print, waiting for USB disconnect, and ending
USB selection. Their selected paths prepare fields or call local helpers; none
of the bodies directly calls the transition owner or contains an established
interface teardown, session close, MTP start, or automatic re-enumeration.

The disconnect-labelled body requests only states 11, 17, 15, or 6 under its
current mode and helper results, then calls the transition owner. It never
requests state 20. The separate caller maps receiver field `+0` values 178 or
179 to state 22, 180 to state 23, and 181 to state 21 before its direct owner
call. No accepted source binds either receiver to a physical disconnect input.

An adjacent range-only event family adds a conditional path into the interior
of the disconnect-labelled body, plus exact owners for two internal globals:

| Role | Local address | Block | Offset | Length |
|---|---:|---:|---|---:|
| Flag clear/get/set leaves | `0x6efc9054` | 0 | `0x009c9074` | 36 |
| Selected flag-setter caller | `0x6efc912f` | 0 | `0x009c914f` | 25 |
| Event-field dispatcher | `0x6efd39ce` | 0 | `0x009d39ee` | 218 |
| Mode-state mapper | `0x6efd3ab3` | 0 | `0x009d3ad3` | 92 |
| Mode-state store leaf | `0x6efd3b0f` | 0 | `0x009d3b2f` | 9 |
| Mode-state load leaf | `0x6efd3b18` | 0 | `0x009d3b38` | 9 |

These spans use the same conditional CODE-local view and add no canonical
instruction rows. The flag leaves clear `0x6066a53c` and `0x6066a540`, read
`0x6066a53c`, or write literal 1 to `0x6066a53c`. The selected setter caller
passes entry `a1` through saved `a2`, calls the setter, then writes 306 at
receiver `+76` and 1 at receiver `+84`. The flag's physical meaning, clearer
input, lifetime, and relationship to the transition receiver remain unresolved.

The dispatcher initially copies entry `a1` to `a3`, but two later direct calls
with empty encoded preservation masks intervene before current `a3` is used.
It then reads current field `a3+4` and clears that same current field. This
establishes field direction for the current object, not preservation of the
entry receiver. The read value maps as follows: 240 calls the mode-state
mapper; 241 maps to 1; 242 to 2; 243 to 3; 244 to 4; 245 to 6; and unmatched
values to 1. Each fixed arm calls the exact store leaf for `0x6066a670`.

The mode-state mapper can write 0, 1, 2, 3, or 4 to `0x6066a670` under its
current helper results, and the exact load leaf returns the current global.
These numeric producers are internally established but have no source-proved
USB, interface, or shooting meaning.

The dispatcher's interior call into the disconnect-labelled body occurs only
when a separate virtual-slot-`+40` call returns current value 1. Event 243
instead skips a later helper/indirect-call pair; that value alone does not
select the interior call. Although the state-19 record mapper writes `+4=243`,
no accepted writer-to-dispatcher edge or common object identity joins that
record to the current dispatch object.

The first missing join is therefore a source-authenticated physical USB or
interface-release owner of the dispatcher's incoming event object, including
receiver preservation through the intervening calls, reaching an accepted
`PC_RETURN` or `PC_CAM_SHOOTING` transition. Active-interface teardown,
ordinary shooting, MTP re-entry, capture, image production, and host transfer
remain unproved.

**Next evidence:** [USB/shooting-state research](../RESEARCH.md#r-usb-shooting-state).

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

**Next evidence:** [USB/shooting-state research](../RESEARCH.md#r-usb-shooting-state)
and [PTP ingress research](../RESEARCH.md#r-ptp-ingress).

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

**Next evidence:** [PTP ingress research](../RESEARCH.md#r-ptp-ingress) and
[USB/shooting-state research](../RESEARCH.md#r-usb-shooting-state).

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

**Next evidence:** [PTP ingress research](../RESEARCH.md#r-ptp-ingress),
[queued-storage research](../RESEARCH.md#r-ptp-storage), and
[USB/shooting-state research](../RESEARCH.md#r-usb-shooting-state).

<a id="registration"></a>
## Registration callers and unresolved callback placement

Caller arguments supply two keys and callback literals. The callbacks' source
placement and runtime selection remain unresolved.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Caller pair | `0x6f330528` | 0 | `0x00d30548` | 36 |
| Builder | `0x6f3349de` | 0 | `0x00d349fe` | 77 |
| First candidate callback span | `0x6f339244` | 0 | `0x00d39264` | 5 |
| Second candidate callback span | `0x6f3393c5` | 0 | `0x00d393e5` | 150 |

The 36-byte block-0 caller span `[0x00d30548,0x00d3056c)` has ten reviewed
instructions under local address view `0x6f330528..0x6f33054c`. It supplies
keys `0x100c` and `0x100d` in `d0`, each with `d1=2`, `a1=0`, and respective
callback literals `0x6f33a684` and `0x6f33a805` in `a0`, then calls local
`0x6f3349de` (source `0x00d349fe`). This establishes static caller arguments,
not runtime registration or host command selection.

The 77-byte builder range at `0x00d349fe` and helper ranges at `0x00d35440` (98
bytes), `0x00d354d9` (32), `0x00d354f9` (40), and `0x00d35521` (38)
authenticate the surrounding allocation and list operations. Source branch
`0x00d34a15` takes a zero lookup result to allocation; `0x00d34a2a` takes a
nonzero allocation result to initialization. The builder copies incoming `d1`
into `d3` before calls and later stores `d3` at node `+2`, but the allocator's
transitive calls do not establish preservation of `d3`. The caller value 2 is
therefore not established as the stored metadata.

Additional spans at source `0x00d39264` (5 bytes) and `0x00d393e5` (150 bytes)
have three instruction rows under local views `0x6f339244` and `0x6f3393c5`.
Mapping the callback literals to these spans by subtracting `0x6e601420`
remains a hypothesis: the singleton module's established delta does not prove
placement of this distinct module. In the latter source span, the mismatch
branch at `0x00d3941e` reaches intermediate status block `0x00d3942e`; the
complete call at `0x00d39469` targets source `0x00d34b57`. Neither the source
coverage nor these local decodes establish callback identity, payload
ownership, helper preservation, capture, or host delivery.

**Next evidence:** [Place the registration
callbacks](../RESEARCH.md#r-ptp-registration).

<a id="fifo"></a>
## Record initialization and FIFO layout

**Established effect:** the decoded caller clears 256 bytes of record storage
beginning at `0xa07b81cc`.

The consumer's first canonical instruction at `0x6f3307f5` is
`movm [d2,d3,a2,a3],(sp)` (block 0, offset `0x00d30815`, length 2). Its load
at `0x6f3307fa` is `mov -1602518580,a3` (offset `0x00d3081a`, length 6): the
signed decimal operand represents runtime address `0xa07b81cc`.

```text
caller: block=0 offset=0x00d30925 length=41
        sha256=3211fdb645a1beb403b214d28add1330dc68ecda34742d4de18c669b2f38dfb5
helper: block=0 offset=0x0010cc15 length=15
        sha256=ebd2aaafb2640932096d3f028009e1c52d9e5a230ccfa93d75717fc991c32ef3
```

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

`0x6f330fba` appends 16-byte records to the array beginning at `0xa07b81cc`;
`0x6f3307f5` consumes the front record and compacts the remainder. The halfword
at `0xa07b82cc` is the live count for at most 16 records, not a completion
flag.

Adjacent halfword `0xa07b82d0` is co-reset with the FIFO and is later used as
the unsigned dividend of a caller-supplied divisor. It is not referenced by the
reviewed append, shift, drain, or completion paths, while the FIFO has a
separate count halfword. Its unit and lifecycle remain unknown; queue-count or
completion-status meanings are unsupported.

**Unresolved:** later contents and lifetime, the upstream request owner, and
runtime execution of this initialization.

[Reproduce the initializer and byte-fill
helper](../ANALYSIS.md#reproduce-the-mapped-ptp-windows-with-gnu-binutils).

**Next evidence:** [Connect the primary request owner to
ingress](../RESEARCH.md#r-ptp-ingress).

<a id="request-selector"></a>
## Primary request selector and caller

The request selector dispatcher at `0x6f32d60c` reads the halfword at `a1+8`.
Its eight numeric arms reach `0x1001` at `0x6f32d683`, `0x1002` at
`0x6f32d6e4`, `0x1003` at `0x6f32d746`, `0x1004` at `0x6f32d7f3`, `0x1005`
at `0x6f32d86f`, `0x1006` at `0x6f32d8e6`, `0x1007` at `0x6f32d94f`, and
`0x1008` at `0x6f32d985`. Reviewed `0x1001`, `0x1002`, `0x1007`, and
`0x1008` paths construct or publish 12-byte descriptors through `0x6e61fd8d`.
The `0x1005` path at `0x6f32d891` and the `0x1006` path at `0x6f32d8fa`
/`0x6f32d900` also load pointer global `0xa07b7058` into address registers.
This is a static software-dispatch relationship, not proof of live request
admission, operation meaning, capture, or transport completion.

The nearest authenticated caller spans `0x6f32d51a..0x6f32d5f8`. It builds
stack-local records, calls `0x6e61fc4b`, conditionally calls `0x6f32dc63`,
then passes the stack-derived `a2` as selector argument `a1` and `d2` as
selector argument `d0`. Under this caller's local source relation,
`0x6f32dc63` maps to block-0 offset `0x00d2dc83` and is a 33-byte status
adapter: it writes two words through `a0`, calls `0x6e61fd33`, conditionally
calls `0x6e682eea` for a negative status, and returns the original status in
`d0`. Other accepted source spans carry the same runtime address under
different local views and do not identify this caller's target body.

`0x6e61fc4b` has two direct calls to the complete 32-byte routine at
`0x6e689567`. That routine sets `a0=d2` before calling the complete 85-byte
body at `0x6e6861ea`. The body writes zero to `a0+64`, initializes several
other fields, links two pointer fields, conditionally calls `0x6e6860f7`, then
calls `0x6e687d3c` and returns. The caller's later read of `d2+64` therefore
observes the established zero initialization before it calls `0x6e68419f`. The
pointed-to object owners, direct-callee contracts, and any join to a transport
receive path remain unresolved.

**Next evidence:** [Connect the primary request owner to
ingress](../RESEARCH.md#r-ptp-ingress).

<a id="selector-vectors"></a>
## Neighboring source vectors and the 0x5001 selector

The source-vector span at block-0 `[0x00d58918,0x00d58988)` is authenticated in
full: 112 bytes, or 28 four-byte entries. It shares its final 40 bytes with the
previously authenticated range beginning at `0x00d58960` and ends where the
adjacent vector at `0x00d58988` begins. The accepted indexed load at
`0x6f333527` names runtime base `0x6f359d38`, distinct from `0x6f359da8`
below. Source authentication alone does not establish runtime table placement,
selection, ownership, or a live request path.

A distinct dispatcher at `0x6f33362c` accepts selectors `0x5001..0x501c`,
subtracts `0x5001`, scales the result by four, and indexes the target vector
at runtime base `0x6f359da8`. The complete 28-word vector is authenticated at
block-0 offset `0x00d58988`; slot 0 contains `0x6f334a8c`. The enclosing
38-word vector at `0x00d58960..0x00d589f7` is also authenticated and includes
neighboring value `0x6f334aef`. The first target builds a stack descriptor and
calls `0x6e61fd8d` at `0x6f334aab`; the sibling body sets `d0=2` at
`0x6f334acf` and calls the same handoff at `0x6f334aef`. The vector
relationship does not establish a common entry ABI. These are static selector
and neighboring-target facts, not proof of the dispatcher's runtime owner, a
live `0x5001` selection, ingress, serialization, or wire completion.

**Next evidence:** [Establish selector-vector placement and
entry](../RESEARCH.md#r-ptp-vectors).

<a id="status-callbacks"></a>
## Status dispatcher and installed callbacks

A caller-side branch at `0x6f32d597` reaches dispatcher `0x6f32d9dc`. Its
branches interpret record `+8` as a status:

| Status | Landing point | Selected routine |
|---:|---|---|
| 0 | `0x6f32d9f1` | Descriptor builder `0x6f32da0e` |
| 1 | `0x6f32d9f8` | Bounded body `0x6f32da3f..0x6f32daca` |
| 2 | `0x6f32d9ff` | `0x6f32dacd` |
| 3 | `0x6f32da06` | `0x6f32dae1` |

The status-0 builder reaches `0x6e61fd8d`. Within the status-1 routine, four
direct calls reach the complete leaf at `0x6f32db27`; it returns the unsigned
halfword read from `0x60355a2c` in `d0` without writing `d2`.

The same routine loads the pointer at `0xa07b702c` and calls it indirectly at
`0x6f32dab1`. The setup sequence stores `0xa07b7044` in pointer global
`0xa07b7058`, so the status-3 path's store of firmware-resident receiver
`0x6f3581f0` at record field `+12` resolves statically to `0xa07b7050`; the
same receiver is later passed as callback context. Three direct reads of
`0xa07b7058` are established in the selector arms above. This is an owner-side
static alias and continuation; allocation, runtime ordering, scheduling, live
ingress, and response behavior remain unproved.

### Callback installation and distinct entry contracts

The complete containing initializer spans `0x6f32f6b5..0x6f32f864`; its suffix
at `0x6f32f824..0x6f32f862` directly calls `0x6f3391d0` at `0x6f32f848` and
`0x6f33c8f5` at `0x6f32f856`. The first path writes `0x6f33aa63` to
`0xa07b702c` through setter `0x6f32d5f8`; the second writes `0x6f33e38f` to
separate global `0xa07b7030` through `0x6f32d602` and installs `0x6f33e485`
into `0xa07b81a0`.

The reviewed `0x6f33e38f` entry fixes `d2` and its return value at 24, reaches
helper `0x6e6050e5`, and returns through a 32-byte cleanup; the helper's
nonzero `0x8050` path builds a size-128 descriptor and hands it to `0x6e61fd8d`.

This differs from the record-populating shape of `0x6f33aa63`; at that
installed entry, the unconditional branch at `0x6f33aaa6` skips the interior
`0x6f33aaad` selector and its call to `0x6f33362c`. No accepted predecessor
selects that interior entry, so adjacent registration does not join the
installed callback to the `0x5001..0x501c` dispatcher or prove a shared
callback signature.

The last target `0x6f33e485` instead tests caller-supplied `d2`, conditionally
reaches a diagnostic-looking helper, and returns `d2`. Canonical block-0
instruction rows contain no direct load of `0xa07b7030`; runtime ordering and
ownership, the contract installed through `0xa07b702c`, and any indirect or
runtime-built consumer of `0xa07b7030` remain unresolved. PTP namespace
constants and local labels support a PTP-adjacent module attribution, but no
RTOS task entry or operation-code ingress is established.

**Next evidence:** [Resolve status callbacks and the skipped interior
entry](../RESEARCH.md#r-ptp-status).

<a id="submitted-record-consumer"></a>
### Adjacent submitted-record consumer candidate

Four instruction-covered islands extend the initializer and an adjacent body.
They establish fixed record setup and a conditional polling/dispatch loop, but
not a complete consumer body, live task entry, or identity with the separate
MTP receive-record submitter.

| Role | Local span | Block | Source span |
|---|---|---:|---|
| Initializer setup A | `[0x6f32f745,0x6f32f75d)` | 0 | `[0x00d2f765,0x00d2f77d)` |
| Initializer setup B | `[0x6f32f7fd,0x6f32f814)` | 0 | `[0x00d2f81d,0x00d2f834)` |
| Adjacent-body entry | `[0x6f32f865,0x6f32f893)` | 0 | `[0x00d2f885,0x00d2f8b3)` |
| Conditional loop | `[0x6f32f97d,0x6f32f9b4)` | 0 | `[0x00d2f99d,0x00d2f9d4)` |

The 52 canonical instructions completely cover these four islands under local
view `source + 0x6e600fe0`. The containing source ranges were already
authenticated. No canonical instructions cover the intervening adjacent-body
span `[0x6f32f893,0x6f32f97d)`, and branch target `0x6f32f9b4` is outside the
last island.

Initializer setup A loads the halfword through `0x6e691ad8`, supplies fixed
arguments `d1=2` and `a1=16`, and calls `0x6e61fd03` with
`a0=0x6f358649`. Setup B loads halfwords through `0x6e691ad8` and
`0x6e691a00`, supplies `a0=32`, and calls `0x6e61fe35`. Missing instructions
between these islands and the initializer's later calls prevent a complete
construction or retained-object contract.

The adjacent body begins at `0x6f32f865`, creates stack pointers at `sp+8`,
`sp+12`, `sp+28`, and `sp+44`, stores -1 at `sp+4`, and calls
`0x6e61fc4b` with `a0=sp+8`, current halfword-derived `d0`, `d1=123`, and
`a1=1`. It then reads the current word at `sp+8`; the uncovered span prevents
carrying that value unconditionally to the later island.

At `0x6f32f97d`, the later island rereads current `sp+8` and tests mask 32.
The clear arm leaves for `0x6f32f9b4`. The set arm places the `sp+12` pointer
at `sp+28`, calls `0x6e61fd33` with the halfword through `0x6e691ad8`,
`a0=sp+28`, and `d1=0`, and leaves on a current nonzero return. A zero return
calls `0x6f3311e7` with current `a0=sp+12`, repeats the same
`0x6e61fd33` call, and branches back to `0x6f32f99a` while its current return
remains zero. The uncovered exit, helper effects, scheduling, termination, and
record ownership remain unresolved.

The reused halfwords and `0x6e61fd33` helper are static commonalities, not proof
that this body consumes the record built by the [MTP submitter](#mtp-event-pump)
or the known FIFO. It does not establish host ingress, event identity, shooting,
capture, image ownership, USB submission, or completion.

**Next evidence:** [PTP ingress research](../RESEARCH.md#r-ptp-ingress),
[status-callback research](../RESEARCH.md#r-ptp-status), and
[queued-storage research](../RESEARCH.md#r-ptp-storage).

<a id="handler-banks"></a>
## FIFO handler banks and candidate writers

The FIFO consumer at `0x6f3307f5` calls `0x6f33093e`; when global `0x8050` is
nonzero, its helper builds a stack descriptor with a size word of 128 and
passes it through `0x6e61fd8d` to the dynamic storage routine at `0x6e68939a`.
The fixed path then uses record `+8` as a sequence value, advances it modulo
16, and probes 16 eight-byte slots in `[0x6f358d44,0x6f358dc4)`. Each matching
slot holds the full sequence at `+0` and a handler at `+4`; control stops at
the indirect jump at `0x6f3309c6`.

**Source placement.** The apparent same-view source coordinate `0x00d58d44` is
authenticated non-table data, and the static dispatch records at `0x00d589f8`
are a distinct structure.

**Candidate writers.** Paired routines at `0x6e681503` and `0x6e68150d` write
`d1` at `a0+20+8*d0` and `a0+24+8*d0`; their established callers supply both
fields for the same indices.

Complete caller ranges are authenticated at `0x6e68002c` (120 bytes),
`0x6e680246` (98 bytes), `0x6e68042c` (114 bytes), and `0x6e6809b8` (97 bytes).
Each saves incoming `a1` in `a2` and supplies it in `a0` to the paired writers;
none establishes a concrete address for that incoming object. The second fields
contain constants `0x1000`, `0x8000`, or zero, without an established
executable handler identity.

**Unresolved base.** This geometry is compatible with the 16-slot table if the
incoming base is `0x6f358d30`, but no accepted instruction establishes that
alias or its runtime owner. This proves a candidate materializer shape, not
table ownership, serialization, endpoint submission, DMA, or wire completion.

**Search banks.** Each bounded search probes 16 eight-byte slots:

| Search | Bank start |
|---|---|
| Initial | `0x6f358d44` (exclusive end `0x6f358dc4`) |
| Status 0 | `0x6f358cc4` |
| Status 1 | `0x6f358c44` |
| Status 2 | `0x6f358bc4` |
| Status 3 | `0x6f358b44` |

The status getter at `0x6f3311b2` reads the unsigned halfword at `0xa07b81a4`.
Each search starts at the low four bits of the incremented record `+8` value,
compares the full value at slot `+0`, wraps at the bank end, and jumps through
matching slot `+4`; a zero key exits the search. In particular, status 2
reaches the search at `0x6f330b16` and indirect jump at `0x6f330b4d`. The four
other same-view source windows at block-0 offsets `0x00d58b44`, `0x00d58bc4`,
`0x00d58c44`, and `0x00d58cc4` are authenticated for 128 bytes each; their
hashes do not establish runtime bank contents. No accepted producer establishes
a slot containing callback landing `0x6f330b53`.

**Next evidence:** [Identify the handler-bank producer and
selection](../RESEARCH.md#r-ptp-handler-banks).

<a id="callback-body"></a>
## Record route through the callback body

The complete 123-byte body `[0x6f330ec2,0x6f330f3d)` preserves its incoming
record pointer in `a2`. When byte `0xa07b81c8` is nonzero, it passes record
fields `+0`, `+4`, and `+12`, with `d1=0xbb02`, to `0x6f33113f`, clears
`0xa07b81b8`, and calls `0x6f331166` at `0x6f330f00`. That call saves `d2`;
the helper's `ret [d2],8` restores the incoming value despite its internal
`mov d0,d2`. The body then loads `0xa07b81a0` and invokes it at `0x6f330f0b`.
The zero-guard branch instead copies 16 bytes from the record to `0xa07b81a8`
and sets bytes `0xa07b82d7` and `0xa07b82d6` to one. The consumer at
`0x6f3307f5` initializes `d2` to its post-prologue `sp+12`; its calls to
`0x6f33093e` supply either fixed FIFO base `0xa07b81cc` (`0x6f330821`) or that
local frame object (`0x6f330889`). The target arm at `0x6f330b53` forwards the
selected record to `0x6f330ec2`. These are bounded object routes and a local
callback register contract; the runtime table contents and selection of that
arm remain unproved. They do not join this callback to the primary selector's
descriptor output or establish a live operation handler.

**Next evidence:** [Identify the handler-bank producer and
selection](../RESEARCH.md#r-ptp-handler-banks).

<a id="reply-storage"></a>
## Reply packing, queued storage, and buffer pool

The five reviewed `0xbb02` literal sites establish one bounded reply lifecycle:
a 16-byte request layout, selector dispatch through record `+8`, normal FIFO
compaction, an exceptional tail-pop drain, 12-byte reply packing, and an
unsigned-halfword return. The tag's product-level name and wire-level
completion remain unproved.

On the out-of-range-selector path, `0x6f33113f` uses record `+0` as a dynamic
handle and constructs a 12-byte stack payload from the input halfword tag plus
record fields `+4` and `+12`. It passes that payload through `0x6e61fd8d` to
`0x6e68939a`, which copies it into dynamic queued or circular storage. Bytes 2
and 3 are not initialized by the builder. This proves a buffer-copy path, not
USB/wire completion.

Accepted coverage continues the storage corridor at `0x6e6893ae` through
pointer walks rooted at table `0x8ff00004`. The current `0x8050` value makes
one four-byte-indexed selection. A second index is derived as
`(d0 & 0x7000) >> 12`; its selected owner's `+0x3c` field supplies a queue
pointer, and queue `+0x1a` supplies an unsigned halfword bound. A source-only
leaf at block-0 offset `0x000a9736` can store incoming `a1` at owner `+0x3c`,
but its runtime address, caller, and the queue allocation are unresolved. These
are static storage and field-level boundaries, not an operation ingress or a
wire-level completion proof.

Nearby routines `0x6f334b0e` and `0x6f334b37` form a two-entry static buffer
pool. Checkout first-fit reserves one of two `0x40000`-byte backing buffers
and returns its pointer or null; release matches that pointer and clears the
descriptor's availability halfword. Routine `0x6f334b5e` is a separate stateful
consumer, not another release primitive.

**Next evidence:** [Identify queued storage and its
consumer](../RESEARCH.md#r-ptp-storage).

<a id="descriptor-owner"></a>
## Descriptor operations and owner-state fields

Two operations depend on owner state and write owner fields. The fields'
consumer and payload identity remain unresolved.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Entry guard | `0x6e74c410` | 0 | `0x0014c430` | 21 |
| Dispatcher | `0x6e74c425` | 0 | `0x0014c445` | 112 |
| First operation | `0x6e74c631` | 0 | `0x0014c651` | 73 |
| Second operation | `0x6e74c67a` | 0 | `0x0014c69a` | 257 |

The descriptor target's entry at `0x6e74c410` covers 21 bytes at block-0 offset
`0x0014c430`. It tests the unsigned owner-relative halfword at `+138` with
mask `-8` and returns `0x7301` on the nonzero arm. Its zero arm continues into
the reviewed dispatcher at `0x6e74c425..0x6e74c495`. That span and operation
bodies `0x6e74c631..0x6e74c67a` and `0x6e74c67a..0x6e74c77b` have full-width
instruction coverage over 442 bytes, at block-0 offsets `0x0014c445`,
`0x0014c651`, and `0x0014c69a` respectively. All ends are exclusive; the
return at `0x6e74c492` is three bytes and ends at `0x6e74c495`.

The dispatcher distinguishes the descriptor's outer `+0` switch from its nested
`+2` switch. Outer `+0=1` with nested `+2=1` or `2` calls `0x6e74c631` at
`0x6e74c468`; outer `+0=2` instead calls `0x6e74c67a` at `0x6e74c474`. On
success it ORs the outer selector into the owner state halfword. These are
distinct operations: a later outer-2 invocation may inherit state from an
earlier outer-1 operation.

The first body copies owner fields `+4` and `+8` into `+24` and `+28`, calls
`0x6e8d9b7d`, and checks the halfword at owner `+96` for nested selectors 1
and 2. The second body requires bit 0 in owner `+138` and conditionally writes
derived values to owner `+112`, `+116`, and `+120`, with a result halfword
at `+124`. Its paths depend on helper results and preexisting owner state.
These static field writes do not establish the helpers' complete behavior, a
selected runtime owner, image/file identity, capture, USB/PTP submission, or
wire completion. No immediate consumer of the resulting owner fields is
established by these spans.

**Next evidence:** [Find the descriptor owner's output
consumer](../RESEARCH.md#r-descriptor-consumer).

<a id="callback-objects"></a>
## Separate callback object family

**Guarded registration and consumption.** A separate setter at `0x6e6a9707`
checks owner field `+0x1c`. When clear, it stores callback `a1` at `+0x3c`,
context `d0` at `+0x48`, and returns the loaded zero guard; otherwise it
returns `0x9a000201` (rendered as signed decimal `-1711275519`). Its paired
consumer at `0x6e6a9720` returns without dispatch when `+0x3c` is null, or
loads context `+0x48` and calls the stored target indirectly.

Direct caller fragments at `0x6e6a0abe` and `0x6e6a224e` load the proposed
callback and context from another object's fields `+172` and `+244` before
reaching the setter. An authenticated caller beginning at `0x6e69ed55` forwards
its incoming object into `0x6e6a0a58`; that path reads an owner candidate from
object field `+288`, then obtains the callback and context from `+172` and
`+244`. A related pair writes an incoming object to field `+288` at
`0x6e6a0783` and later reads the field at `0x6e6a237c` before indirect dispatch
through `0x6e6a224e`.

**Object pairing and callers.** The producer at `0x6e6a0742` binds two incoming
object roles: with `O` in `a0` and `S` in `a1`, its guarded path stores `O` at
`S+0x30` (`0x6e6a077a`) and `S` at `O+0x120` (`0x6e6a0783`), then calls
`0x6e6a224e`. Callback/context values come from `O+0xac` and `O+0xf4`.

Thunks at `0x6e6ae092` and `0x6e6ae95e` load `O` from the pointer field at
`parent+0x24` and call `0x6e6a0742` and `0x6e6a22c1`, respectively; `S`
remains caller-supplied. Their authenticated block-0 spans are
`(offset=0x000ae0b2, length=40)` and `(offset=0x000ae97e, length=40)`; the
latter callee is covered by `(offset=0x000a22e1, length=214)`. Caller rows at
`0x6e6caa8c` and `0x6e6d829e` directly reach `0x6e6ae092` after loading the
source pointer through `a1`; the source class remains unidentified.

**Provider construction.** An authenticated provider-aggregate construction
span at block-0 offset `0x00653ab2` (222 bytes) constructs subobjects at
`outer+0xe8` and `outer+0x1b0`. The setup spans at `0x00653f9d` (8 bytes) and
`0x006540de` (15 bytes), with the setter at `0x00654fe6` (7 bytes), establish
the local relation `O=outer+0x1b0`, `P=outer+0xe8`, and `*(O+0x128)=P`. The
184-byte constructor span at `0x00654340` clears `O+0x128` before later setup
supplies that field.

**Unresolved factory target.** The factory at `0x6e6a0a9d` loads `P=*(O+0x128)`, then calls the function pointer stored at `P+0x20`; there is no intervening
load of a table from `*(P)`. That function pointer remains unresolved.

These local object relations do not establish the concrete source class,
writers of the callback/context values, a concrete callback routine, runtime
ownership or ordering, or a join to the PTP selector, FIFO, ingress, USB, wire,
or camera behavior.

**Next evidence:** [Resolve the separate callback
provider](../RESEARCH.md#r-callback-provider).

<a id="descriptor-tables"></a>
## Unjoined descriptor tables

**17-record descriptor table.** A separate authenticated table at block-0
offset `0x0008f0e0` contains 17 contiguous 28-byte records keyed by `0x1001`,
`0x1002`, and `0x100b..0x1019`. Positional word `+12` is consistently
target-shaped: rows 2 through 12 share `0x6e69e7cb`, while the remaining rows
have bounded target spans under the same local relation. The `0x100e` row's
seven words are `(0x100e, 0, 3, 0x6e69e7cb, 5, 0x1000, 0)`. The shared target
calls `0x6e69d892`, clears the word through `a2`, then dispatches indirectly
through slot `+20` of an object reached from `d2+24`. The complete nine-byte
helper at block-0 offset `0x0009d892` (local address `0x6e69d892`) reads an
unsigned byte from `(d3,a3)` into `d0`, clears `d1` and `d0`, compares `a0`
with 20, and returns. This bounded leaf does not identify the indirect callee
or establish capture, image ownership, or transfer. Authenticated neighboring
lookup families do not identify the consumer. Reviewed local-overlay routines
select between four-byte-indexed bases `0x6e68ef1c` and `0x6e690a50` under
global `0x8050`; other routines first consume distinct 16- and 20-byte
families around `0x6e690708` and `0x6e69081c`. Their geometry is incompatible
with the 28-byte records, while the separate 34-word vector at block-0 offset
`0x00090a98` still has no authenticated code reference. No runtime owner
selects the 17-record table, so it does not add a `0x100e` arm to the primary
selector or prove request admission.

**66-record table with an interior target.** A separate 66-record table at
block-0 offset `0x0008b300` uses 28-byte records. Its key-`0x4e` record points
to `0x6e708fa2`, three bytes into the authenticated body at `0x6e708f9f` and
exactly at the reviewed call to `0x6f33f6dc`. Two other raw four-byte hits
near that body are alignment false positives: bytes `6e 70 90 82` at block-0
offset `0x003a312f` begin inside a little-endian vector word, while bytes
`6e 70 90 08` at `0x0081422a` cross three MN103 instructions in GNU objdump
2.45's decode of the enclosing range. This leaves one static
table-to-interior-entry edge; no accepted evidence identifies the table's
runtime address, owner, selection logic, or indirect invocation.

**Next evidence:** [Find consumers of the unjoined descriptor
tables](../RESEARCH.md#r-ptp-descriptor-tables).

<a id="unselected-entries"></a>
## Handler boundary and unselected alternate starts

A late handler span at `0x6f33fb8e` has an authenticated direct call to
`0x6f33faec` followed by a return, and the established incoming load maps a
selected vector tail into that span. This establishes a static handler
boundary, not runtime reachability, operation meaning, or wire-level
completion.

The uncovered byte starts at `0x6f331e20`, `0x6f331e30`, and `0x6f331e58`
independently decode as `clr d0`, `clr d0`, and `clr d1`. They are alternate
starts at byte gaps between retained canonical rows; no accepted branch, table,
or caller selects them. These decodes do not establish entry identity, runtime
reachability, or handler execution.

**Next evidence:** [Establish entry edges for isolated handlers and alternate
starts](../RESEARCH.md#r-ptp-entry-edges).

<a id="decode-boundaries"></a>
## Current instruction boundaries and alternate decode

The current corpus retains complete instruction widths and a specifically
adjudicated overlapping decode. These are entry-selection pitfalls for the
sections above, not evidence that the paths execute.

| Source region or instruction | Current interpretation |
|---|---|
| `0x6f331fb7..0x6f332029` / source `[0x00d31fd7,0x00d32049)` | 47 contiguous full-width instructions; both range ends are exclusive. Starts inside call operands at `0x6f331ffd` and `0x6f33201b` have no independent alternate-entry support. |
| `0x6f331948`, `0x6f332c7f`, `0x6f332d20` | Six-byte `mov (0xa07b87f0),a0` loads. The former one-byte starts `0x6f33194c`, `0x6f332c83`, `0x6f332d24` lie inside their operands and are not retained as entries. |
| `0x6f33195f`, `0x6f332112`, `0x6f33217d`, `0x6f332c99`, `0x6f332d3d` | Full-width call rows retain their reviewed instruction text and targets. |
| `0x6f331cf3` and ten starts within `0x6f334b62..0x6f334c0b` | Six-byte instructions; stale four-byte rows and malformed one-byte `a0` operand fragments are not retained. |
| `0x6f331cf4` | Independently reproduced five-byte `jmp 0xde68afeb` overlaps the preceding start; its executable entry remains unproved. |
| `0x6f339800` / source `0x00d39820` | Seven-byte call; next instruction `0x6f339807`. |
| `0x6f339854` / source `0x00d39874` | Five-byte call; next instruction `0x6f339859`. |
| `0x6f33a8e0` / source `0x00d3a900` | Five-byte call; next instruction `0x6f33a8e5`. |
| `0x6f333527` / source `0x00d33547` | Six-byte `mov 1865784632,a1`; next instruction `0x6f33352d`. |

Correction rationale and replacement counts remain in Git/PR history. See
[contextual verification](../DECODING.md) and the [correction regression
fixtures](../../tests/fixtures/decode-regressions/README.md). Complete widths
do not establish register preservation through the calls.

**Next evidence:** [Establish entry edges for isolated handlers and alternate
starts](../RESEARCH.md#r-ptp-entry-edges).
