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
- [Registration callers and unresolved callback placement](#registration)
- [Record initialization and FIFO layout](#fifo)
- [Primary request selector and caller](#request-selector)
- [Neighboring source vectors and the 0x5001 selector](#selector-vectors)
- [Status dispatcher and installed callbacks](#status-callbacks)
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
