# Open firmware research

Choose a question below, read its linked finding, and submit authenticated
evidence through [CONTRIBUTING.md](../CONTRIBUTING.md). The
[firmware map](FIRMWARE_MAP.md) summarizes what is established;
[reading conventions](firmware/READING.md) explain addresses and claim limits.

The practical request-to-image question is how a host request could select a
controllable handler, initiate a still capture, identify its image, and return
that image to the host. The release-control candidates provide input and caller
boundaries to investigate. Image ownership and host transport remain separate
missing connections. The questions below are durable evidence gaps, not a live
work queue; overlapping contributions and well-supported negatives are useful.

[Historical observations](FIRMWARE_MAP.md#observed-capabilities) already establish
specific modified-image deployment and existing-JPEG retrieval. The remaining
target is a new host-initiated capture connected to that retrieval capability,
not rediscovery of basic download or proof that any modified image can boot.

**Status:** Open means the question is unresolved; Narrowed means reviewed
findings settle part of its scope; Answered requires a linked result that
settles its stated scope. These labels do not measure capture-path completion.

## Choose a starting point

| Interest | Questions |
|---|---|
| First contribution | [Extend a supported boundary](#r-first-contribution) |
| Release interface and inputs | [Release and guarded action](#r-release-contract), [caller record](#r-caller-record), [frontend inputs](#r-release-inputs), [key owner](#r-key-owner) |
| Still-object ownership | [List consumer](#r-still-list), [nested receiver](#r-still-receiver), [field +100](#r-still-field-100) |
| Live view and scalar records | [Frame owner](#r-live-view-owner), [ThroughImage record](#r-throughimage-record) |
| PTP-adjacent ingress and dispatch | [Registration](#r-ptp-registration), [request owner](#r-ptp-ingress), [vectors](#r-ptp-vectors), [status callbacks](#r-ptp-status), [handler banks](#r-ptp-handler-banks) |
| Storage and unjoined objects | [Queued storage](#r-ptp-storage), [descriptor consumer](#r-descriptor-consumer), [callback provider](#r-callback-provider), [descriptor tables](#r-ptp-descriptor-tables), [entry edges](#r-ptp-entry-edges) |
| USB state and lifecycle | [State owner](#r-usb-state-owner), [policy provider](#r-usb-policy-provider), [event owner](#r-usb-event-owner), [communication receivers](#r-usb-communication-receiver), [MTP selection](#r-mtp-selection), [record owner](#r-mtp-record-owner) |
| Hardware integration | [USB shooting state](#r-usb-shooting-state), [new-image retrieval](#r-capture-retrieval) |
| Layout and startup | [Address mappings](#r-address-mapping), [boot chain](#r-startup), [block 1](#r-block-1), [block 2](#r-block-2), [block 3](#r-block-3), [block 4](#r-block-4), [integrity](#r-integrity) |
| Unassigned anchors | [Caller context](#r-unassigned-caller), [receiver prologue](#r-unassigned-receiver) |

<a id="r-first-contribution"></a>
## Extend a supported instruction boundary

**Start from:** a canonical caller or control-flow edge in a
[mapped area](FIRMWARE_MAP.md#established-regions), after checking current
coverage. The [analysis workflow](ANALYSIS.md) includes a reproducible example.

**Useful result:** a complete, authenticated continuation to a branch, return,
indirect call, or existing boundary. Explain its relevance and any decoder or
entry ambiguity in the PR. Another isolated decode of an already mapped body
does not resolve its owner or execution path.

<a id="r-release-contract"></a>
## Resolve the release-control body's indirect consumers

**Status:** Narrowed.

**Question:** which of the separate candidate entry points reaches an actual
capture or image-producing effect with established receiver and input contracts?

**Established:** reviewed guards, construction joins, and native argument
formation narrow individual boundaries. Their detailed contracts live in
[release control](firmware/RELEASE_CONTROL.md), the
[constructed service](firmware/RELEASE_SERVICE.md), and
[still-object methods](firmware/STILL_OBJECTS.md).

Choose the [release-body](#r-release-body-effect), [action/carrier](#r-action-carrier),
[service receiver](#r-release-service), [conditional endpoint](#r-release-endpoint),
[native request](#r-native-still-request), or [native still-take](#r-native-still-take) question.

**Useful result:** answer one of these independent questions and connect its
effect to the relevant capture or payload observation. A scalar return or
diagnostic label alone does not identify that effect. This umbrella remains open
until the required connection is established; it is not a shared object identity.

<a id="r-release-body-effect"></a>
## Identify the release body's selected consumers

**Status:** Open.

**Question:** which concrete receivers and input profiles reach the conditional
lookups and helper `0x6ebd9652`, and what effect follows?

**Start from:** [release body and direct callers](firmware/RELEASE_CONTROL.md#release-body).

**Useful result:** follow an authenticated entry through argument definitions
and call preservation to a selected consumer and its effect. Distinguish complete
range coverage from the sparsely recorded caller instructions.

<a id="r-action-carrier"></a>
## Resolve the guarded action's state and carrier methods

**Status:** Open.

**Question:** who owns the tested bit-state object and the dynamic receivers
used after the two guards permit continuation?

**Start from:** [guard outcomes and carrier calls](firmware/RELEASE_CONTROL.md#guarded-action).

**Useful result:** establish the bit producers, valid pointee and clear-bit
conditions, then resolve the carrier/returned-receiver contracts through the
dynamic methods. Preserve the writer's separate null-safety boundary and the
distinction between the saved carrier and the slot-`+16` result.

<a id="r-release-service"></a>
## Establish the service's live receiver and method

**Status:** Open.

**Question:** which valid, live receiver does the cached service select, and
what does its table slot `+4` do?

**Start from:** [constructed service and receiver selection](firmware/RELEASE_SERVICE.md#constructed-service).

**Useful result:** connect the qualified construction/cache-store identity to
the later cache reload, current field `+140`, and selected method. Resolve
pointed-storage effects and scalar preservation through slot `+156`.
Initial zero writes and the root's distinct wiring fields do not settle those
later values or equate the service with the action's carrier.

<a id="r-release-endpoint"></a>
## Establish the conditional endpoint's objects and effects

**Status:** Open.

**Question:** are the nominated endpoint and table selected with valid live
objects, and what do the first unresolved methods do?

**Start from:** [endpoint branches](firmware/RELEASE_SERVICE.md#conditional-receiver-endpoint)
and [shared continuation](firmware/STILL_OBJECTS.md#continuations).

**Useful result:** bind entering E/P/Q and the conditional table, then establish
method effects, storage lifetime, and preservation on the selected arm. Keep
the loaded-global branch separate from pointer P and its method return.
The qualified gate-clear join stops at Q-table `+40`; gate-set also needs
Q-table `+8`. Native record formation does not prove a call to this endpoint,
safe record retention, or capture completion.

<a id="r-native-still-request"></a>
## Identify the native still-request method's effect

**Status:** Open.

**Question:** what receives the native request body's indirect call, and does
that method actually publish a request or initiate capture?

**Start from:** [native still-request boundary](firmware/STILL_OBJECTS.md#native-still-request).

**Useful result:** bind the current field-`+140` receiver, slot `+4`, and
constructed argument through intervening helpers. Preserve the immediate-return
predicate arm. The diagnostic after the call does not establish its effect.

<a id="r-native-still-take"></a>
## Identify a capture effect in the native still-take body

**Status:** Open.

**Question:** what downstream effect follows the established scalar handoff?

**Start from:** [native still-take boundary](firmware/STILL_OBJECTS.md#native-still-take).

**Useful result:** select a bounded call with complete argument and preservation
support and identify its capture or object effect. The authenticated full-body
range has sparse canonical instruction anchors; the phase name and normal
return are insufficient.

<a id="r-caller-record"></a>
## Identify the caller record's owner and consumers

**Status:** Open.

**Start from:** the [caller and record-writing body](firmware/RELEASE_CONTROL.md#caller-record)
at sources `0x0058d8b3` and `0x005cbbe6`.

**Question:** who supplies and retains the destination, what do its full-width
members represent, and which consumers use them?

**Useful result:** establish the wrapper-returned receiver and destination
preservation through the caller and body helpers; trace a concrete field's
producer, type, consumer, and lifetime. Verify scalar-helper preservation at
source `0x005bee73` separately. Narrowed halfwords and a calculated scalar do
not classify all other fields, and neither record writes nor normal return zero
identifies a captured image or a host-transfer path.

<a id="r-release-inputs"></a>
## Establish frontend input and receiver contracts

**Status:** Open.

**Start from:** the [six-input frontend](firmware/RELEASE_CONTROL.md#six-input-frontend).

**Question:** what is written on conversion failure, and which concrete method
does the returned control object's slot `+304` select?

**Useful result:** establish destination initializedness, the installed table's
data mapping, receiver readiness, and the selected method's consumer. Keep six
current destination words distinct from six successfully parsed inputs; the
frontend's normal zero return is not a capture-success result.

<a id="r-key-owner"></a>
## Connect the candidate key-conversion owner

**Status:** Open.

**Start from:** the [owner candidate](firmware/RELEASE_CONTROL.md#key-conversion-owner)
and [bounded selector-to-key lookups](firmware/RELEASE_CONTROL.md#key-lookup).

**Question:** does this object implement the frontend's conversion contract?

**Useful result:** establish the installed word's table mapping and the source
connection to the frontend, including helper preservation and destination writes
on failure. For the lookup leaves, establish runtime placement of the candidate
key tables and a concrete caller's receiver and selector values. Their bounded
scalar results do not establish parsing, destination writes, or the owner's
connection to the frontend. Code-display arithmetic alone cannot establish data
placement.

<a id="r-still-list"></a>
## Identify the still-corridor list consumer

**Status:** Open.

**Start from:** [singleton dispatch and population](firmware/STILL_OBJECTS.md#singleton).

**Question:** what is the list's runtime class, and which object receives the
later slot-`+20` call?

**Useful result:** a supported producer/consumer connection from the populated
list to that dispatch. Object creation and list append do not establish exposure
or image production.

<a id="r-still-receiver"></a>
## Identify the nested receiver of the +2216 object

**Status:** Open.

**Start from:** the [separate object path](firmware/STILL_OBJECTS.md#owner-2216),
especially the nested call at `0x6ee1d52a`.

**Useful result:** establish the concrete receiver/table and the returned field's
producer or consumer, then test whether it joins the singleton corridor. Preserve
the getter's distinct local and canonical load-address anchors.

<a id="r-still-field-100"></a>
## Trace the pointer stored in field +100

**Status:** Narrowed.

**Start from:** the [getter, writer, and separate table candidate](firmware/STILL_OBJECTS.md#field-100)
and their [dispatch continuations](firmware/STILL_OBJECTS.md#continuations).

**Question:** who supplies the setter's incoming pointer, and which concrete
parent and returned object reach the slot-`+8`/`+48` consumers?

**Useful result:** prove those identities through the calls. The qualified
gate-clear join preserves E/Q and the field-`+100` result through the early
checks, but Q-table `+40` at source `0x0081c771` remains unresolved. At that
call `a0=Q,a1=E`; `a2` has been rebound to the method target, while the
loaded pointer was saved in `a3`. Establish preservation and that pointer's
producer/type/lifetime beyond the call; gate-set also requires the earlier
Q-table `+8` effects. Shared methods do not select a parent table; one table's
slot-`+40` no-op does not resolve Q's call at local `0x6ee1db91`.

<a id="r-live-view-owner"></a>
## Identify the live-view frame owner

**Status:** Open.

**Start from:** the [collection and copy paths](firmware/LIVE_VIEW.md#collections).

**Useful result:** identify the helper's caller-supplied object or the destination
of the three-word copy, then connect it to `outer+132` or a concrete frame handle
and consumer. Previous exact string-address scans did not find an
instruction-aligned owner reference; another vocabulary scan alone is unlikely
to answer the question.

<a id="r-throughimage-record"></a>
## Find the producer of the ThroughImage record

**Status:** Open.

**Start from:** the [scalar lookup](firmware/LIVE_VIEW.md#throughimage) and
[separate initializer](firmware/LIVE_VIEW.md#record-initializer).

**Question:** what populates the array at `0x6034aff0`, and what is the `0x2100`
record's `+4` value?

**Useful result:** authenticate a writer or establish/rule out the initializer
connection with caller arguments and intervening register effects. Follow the
selected value through `0x6e76efc8` / `0x6e76ee46` to a destination write or
payload effect. Matching `0x2100` alone does not join the records; the scalar
return does not identify an image pointer.

<a id="r-ptp-registration"></a>
## Place the registration callbacks

**Status:** Open.

**Start from:** the [registration callers and builder](firmware/PTP.md#registration).

**Useful result:** establish this module's source-to-runtime placement and bind
the callback literals to authenticated entries. Separately establish whether
caller metadata 2 survives the allocator's transitive calls in `d3` to node
`+2`. The singleton module's delta is insufficient for this module.

<a id="r-ptp-ingress"></a>
## Connect the primary request owner to ingress

**Status:** Narrowed.

**Question:** what authenticated transport input selects the reviewed request
owner and supplies its records?

**Start from:** [primary selector and caller](firmware/PTP.md#request-selector),
[initializer and callbacks](firmware/PTP.md#status-callbacks), and the separate
[submitted-record consumer candidate](firmware/PTP.md#submitted-record-consumer).

**Useful result:** establish the runtime owner, scheduling/entry, and preserved
record identity from a transport receive operation into the selected body.
Known working reads and [scoped operation-rejection observations](observations/DEPLOYMENT.md#advertisement)
provide controls. Distinguish the installed callback from its skipped interior
entry and preserve the consumer's uncovered instruction spans.

The [MTP selection](#r-mtp-selection) and [receive-record ownership](#r-mtp-record-owner)
questions cover separate candidate connections. Shared helpers, names, and
source adjacency do not establish that their records are the primary owner's
records. This question remains about ingress, not a complete USB implementation.

<a id="r-usb-shooting-state"></a>
## Distinguish USB mode from shooting-state restrictions

**Status:** Open.

**Question:** is ordinary shooting suppressed by USB personality, an open PTP
session, host interface ownership, or another camera state?

**Start from:** [historical session and capture observations](observations/USB_AND_MEDIA.md#remaining-validation).
Existing-image retrieval is demonstrated within its recorded scope. The static
[state](firmware/USB_STATE.md), [policy](firmware/USB_POLICY.md), and
[lifecycle](firmware/USB_LIFECYCLE.md) findings do not identify an active shooting
restriction; their independent questions follow below.

**Useful result:** first check retained records for a controlled comparison of
actual new-image production. A separately authorized hardware observation could
compare MTP with no open session, an open session, a closed session with the
host interface released but cable attached, and a disconnected shooting control.
Bind image and session conditions. Button or LCD response alone is insufficient.
Such an observation would constrain lifecycle work without identifying a firmware
global or proving host-triggered capture.

<a id="r-usb-state-owner"></a>
## Identify the candidate state bytes' live owner and meaning

**Status:** Open.

**Question:** what selects the byte-writing callback and consumer, and how do
their current values relate to shooting?

**Start from:** [candidate state stores and consumer](firmware/USB_STATE.md#usb-connect-stores)
and the separate [reporting wrapper](firmware/USB_STATE.md#usb-state-wrapper).

**Useful result:** establish live registration/input ownership, preservation
through opaque calls, and a concrete downstream effect. Current post-helper
values and explicit conditional stores do not define persistent globals,
numeric USB states, or the reporting wrapper's value source.

<a id="r-usb-policy-provider"></a>
## Resolve the policy query's dynamic inputs

**Status:** Narrowed.

**Question:** what callback result, list contents, and record status supply
the conditional policy checks at runtime?

**Established:** the [singleton and selected slots](firmware/USB_POLICY.md#singleton-and-selected-query-slots)
and [finite list-value mapper](firmware/USB_POLICY.md#dynamic-list-production-and-the-fourth-word)
are source-joined within their stated address views.

**Useful result:** independently identify the transform callback, the fourth
word's writer/lifetime, or the status source for the selected queries. Preserve
the distinction between literal query inputs and post-callback keys, and between
the first three words' possible values and their current values after the clear
call. Validator polarity depends on context; labels do not give physical meaning.

<a id="r-usb-event-owner"></a>
## Connect a physical input to the USB-labelled event dispatchers

**Status:** Open.

**Question:** what physical USB or interface event supplies a preserved event
object and value to a reviewed dispatcher?

**Start from:** [PC/USB event dispatch](firmware/USB_POLICY.md#state-records-and-event-dispatch)
and the separate [communication-state input](firmware/USB_LIFECYCLE.md#disconnect-input-and-receiver-boundaries).

**Useful result:** authenticate the producer into source `0x009d39ee` or
`0x006cfbd2`, its object identity and preservation, and the selected effect.
State-19 record field `+4=243` alone does not establish the first object's
identity or select its interior call. The reviewed
[USB-labelled name maps](firmware/USB_LIFECYCLE.md#usb-disconnect-name-maps)
stop in resource/formatting paths; extending that bounded negative requires
an independent event-production connection.

<a id="r-usb-communication-receiver"></a>
## Resolve the communication state's effect-bearing receivers

**Status:** Open.

**Question:** which concrete objects and methods perform the candidate close
or start operations?

**Start from:** [communication-state family](firmware/USB_LIFECYCLE.md#communication-cycle).

**Useful result:** bind the current result/table/receiver at the first
owner-candidate slot `+8`, then resolve the end-communication slot `+36` and
connecting/MTP targets. The dispatcher, end-communication, and field-helper
receivers remain distinct. Local preservation through one callee does not
repair the upstream identity gap; slot `+80` is not slot `+36`.

<a id="r-mtp-selection"></a>
## Establish live selection of the MTP lifecycle candidates

**Status:** Open.

**Question:** what live owner selects the named MTP start/end wrappers?

**Start from:** [lifecycle callers](firmware/MTP_LIFECYCLE.md#mtp-communication-lifecycle)
and [aggregate/selector candidates](firmware/MTP_LIFECYCLE.md#mtp-lifecycle-owner).

**Useful result:** prove the state-7 helper's receiver identity and field/table
selection, or an independent incoming edge to a wrapper. Resolve preservation
of the status writer's current `d2` and wrappers' current `a2` before assigning
their effects to entering values. States 6/7 and the separate Boolean-shaped
leaf have no established session or shooting meaning.

<a id="r-mtp-record-owner"></a>
## Identify the MTP receive record's owner and consumer

**Status:** Open.

**Question:** who produces and retains the submitted record, and what consumes
its selected pump-shaped path?

**Start from:** [receive-record submission](firmware/MTP_LIFECYCLE.md#mtp-event-pump).

**Useful result:** establish the record's identity, meaning, scheduling, and
consumer across the uncovered exits and address-view gap. Identify the writer
and lifetime of `0x605fc9dc` before interpreting its bit test. The adjacent
[PTP consumer candidate](firmware/PTP.md#submitted-record-consumer) and
[queued-storage path](firmware/PTP.md#reply-storage) require independent object
connections; shared helpers do not establish delivery or wire completion.

<a id="r-capture-retrieval"></a>
## Associate a new capture with its retrievable image

**Status:** Open.

**Start from:** [verified existing-object retrieval](observations/USB_AND_MEDIA.md#retrieval)
and the [candidate capture consumers](firmware/RELEASE_CONTROL.md#release-body).

**Useful result:** establish a particular capture's new object identity and
readiness, then successful host retrieval of that object under the applicable
USB state. Distinguish an old JPEG, a thumbnail, and a completed new image.
An event or object-list change must be tied to that capture; an import watcher
or software-trigger rehearsal alone does not prove the association. Reuse
the working read path where applicable. A complete reconstruction of unrelated
image-processing internals is not a prerequisite for a bounded observed join.

<a id="r-ptp-vectors"></a>
## Establish selector-vector placement and entry

**Status:** Open.

**Start from:** the [neighboring vectors](firmware/PTP.md#selector-vectors).

**Useful result:** establish source placement and the caller/owner supplying
`0x5001` to `0x6f33362c`. Keep the two runtime bases and neighboring interior
targets distinct. A vector does not establish a common entry ABI.

<a id="r-ptp-status"></a>
## Resolve status callbacks and the skipped interior entry

**Status:** Open.

**Start from:** [status dispatch and callback installation](firmware/PTP.md#status-callbacks).

The [adjacent consumer candidate](firmware/PTP.md#submitted-record-consumer)
adds two initializer setup islands and a separate sparse loop. Determine whether
the initializer retains that body's record owner or schedules its entry; source
adjacency alone is not an execution edge.

**Useful result:** identify the initializer's runtime owner/order, the writer
of `0x60355a2c`, the callback contract through `0xa07b702c`, or a consumer of
`0xa07b7030`. To connect the `0x5001` dispatcher, supply an authenticated
predecessor selecting `0x6f33aaad`; the installed entry at `0x6f33aa63` skips it.

<a id="r-ptp-handler-banks"></a>
## Identify the handler-bank producer and selection

**Status:** Open.

**Start from:** the [paired writers and complete callers](firmware/PTP.md#handler-banks)
and the [callback record route](firmware/PTP.md#callback-body).

**Useful result:** trace the callers' incoming `a1` and prove or rule out its
base being `0x6f358d30`. Establish the executable handler value and the runtime
selection of `0x6f330b53` before claiming a live handler. Field geometry and
the fixed consumer's register route are insufficient without that connection.

<a id="r-ptp-storage"></a>
## Identify queued storage and its consumer

**Status:** Open.

**Start from:** the [reply and storage corridor](firmware/PTP.md#reply-storage).

The separate [receive-record/pump join](firmware/MTP_LIFECYCLE.md#mtp-event-pump) reaches
two pump-shaped helpers but does not identify their queue, storage object, or
USB consumer. Shared vocabulary or nearby source placement is not an object
join. The adjacent submitted-record consumer similarly reuses
`0x6e61fd33`, but its stack-record identity and connection to either storage
path remain unresolved.

**Useful result:** identify the concrete object selected by `(d0 & 0x7000) >> 12`,
its queue allocation, and the caller of the source-only writer at `0x000a9736`,
including the object supplied in `a1`. Then establish the storage consumer.
A copied reply buffer does not establish USB submission or wire completion.

<a id="r-descriptor-consumer"></a>
## Find the descriptor owner's output consumer

**Status:** Open.

**Start from:** the [owner-state operations](firmware/PTP.md#descriptor-owner).

**Useful result:** authenticate a consumer of owner `+112/+116/+120` and result
halfword `+124`, tracing required state and helper outcomes from the caller.
Keep outer `+0` and nested `+2` switches distinct; a later outer-2 invocation
may inherit outer-1 state. Identify payload type and lifetime before calling
the result an image or file.

<a id="r-callback-provider"></a>
## Resolve the separate callback provider

**Status:** Open.

**Start from:** the [callback object family](firmware/PTP.md#callback-objects).

**Useful result:** resolve the writer/value of `P+0x20`, the parent field's
producer or source class, or same-object writers of `O+0xac` and `O+0xf4`.
The factory calls the pointer stored directly at `P+0x20`; an extra dispatch-table
dereference is unsupported. A connection to a known selector, queue, or transport
owner also needs independent evidence.

<a id="r-ptp-descriptor-tables"></a>
## Find consumers of the unjoined descriptor tables

**Status:** Open.

**Start from:** the [17-record and 66-record tables](firmware/PTP.md#descriptor-tables).

**Useful result:** identify the runtime owner and selection of the 17-record
table, including whether it selects `0x100e`, and resolve slot `+20` of the
object reached from `d2+24`. For the separate key-`0x4e` table, establish its
runtime placement, key selection, and indirect invocation. The neighboring
lookup families and raw alignment false positives do not supply those edges.

<a id="r-ptp-entry-edges"></a>
## Establish entry edges for isolated handlers and alternate starts

**Status:** Open.

**Start from:** the [handler and byte-gap starts](firmware/PTP.md#unselected-entries)
and [current decode boundaries](firmware/PTP.md#decode-boundaries).

**Useful result:** identify the late handler's producer/runtime owner or a
supported caller/table edge selecting an alternate start. Complete instruction
widths and independently reproducible overlapping decodes do not prove entry.

<a id="r-address-mapping"></a>
## Establish a local address mapping

**Status:** Open.

**Start from:** the [coordinate conventions and examples](firmware/READING.md#coordinates).

**Useful result:** authenticate a relationship between decoded offsets, copied
regions, overlays, or runtime addresses, or bound why competing views remain.
An arithmetic match without a supported caller, table, or relocation context
is not placement evidence.

<a id="r-startup"></a>
## Connect the startup chain to reset

**Status:** Open.

**Start from:** the [state accesses](firmware/STARTUP.md#state-access) and
[local overlay handoff](firmware/STARTUP.md#overlay-handoff).

**Useful result:** authenticate a predecessor, initialization owner, task
boundary, or runtime-built pointer connecting the handoff to reset. The bounded
block-0 direct/literal census is already negative; repeat it only with a new
reason it would answer the missing connection.

<a id="r-block-1"></a>
## Resolve block 1's delegated materializer

**Status:** Open.

**Start from:** [block 1's record and request layout](firmware/BLOCKS.md#block-1).

**Useful result:** independently anchor the complete caller context, select the
applicable address view, and follow the service below `0x402e90bc` to a payload
effect that distinguishes copying, DMA, or address mapping. Preserve record 0's
`a3 == 0` condition. Broad structural rescans alone do not identify a consumer.

<a id="r-block-2"></a>
## Find block 2's consumer

**Status:** Open.

**Start from:** [block 2's boundaries and parameter path](firmware/BLOCKS.md#block-2).

**Useful result:** follow the delegated boundary to a payload read, copy,
mapping, or consumer effect. The equality between base-plus-length and a header
word is insufficient. Prior text, packing, compression/transform, cross-block
copy, and canonical-operand searches did not identify a consumer.

<a id="r-block-3"></a>
## Find the block 3 resource consumer

**Status:** Open.

**Start from:** the [JPEG bundle](firmware/BLOCKS.md#block-3).

**Useful result:** connect an index entry or 16-byte record prefix to an
authenticated block-0 read, copy, decode, or display path. Exact extents and
dimensions are established; visual similarity does not establish a UI role.

<a id="r-block-4"></a>
## Resolve block 4's decoder and external owner

**Status:** Open.

**Start from:** the [H8-compatible image](firmware/BLOCKS.md#block-4).

**Useful result:** reproduce the common target at offset `0x122a` with an
independently supported H8 decode, then trace the producer of selector
`0x004003c1`. Investigate whether the block-0 context at `0x00338a80` leads to
a fifth-body descriptor, transfer, or start. The shared literal alone supplies
no such connection, and no block-4 instruction row is canonical.

<a id="r-integrity"></a>
## Establish updater or device authentication

**Status:** Narrowed.

**Start from:** the [host-visible container result](firmware/BLOCKS.md#container-integrity).

**Known:** [specific modified images were deployed and used after boot](observations/DEPLOYMENT.md#modified-image).
One other candidate [failed to boot and was recovered](observations/DEPLOYMENT.md#recovery).
The general validation and loading mechanism remains unresolved.

**Useful result:** independently inspect a verifier, updater/device validation
path, technical documentation, or reproducible static artifact explaining the
applicable checks and limits. Host-parser acceptance of a repaired checksum
alone does not establish device acceptance; the separate hardware successes
do not establish acceptance of arbitrary executable changes. Product pages,
filenames, and requester-side access controls do not resolve the mechanism.

<a id="r-unassigned-caller"></a>
## Establish the unassigned caller's context

**Status:** Open.

**Start from:** the [complete caller span](firmware/UNASSIGNED.md#complete-caller).

**Useful result:** establish an authenticated entry/caller and argument
preservation through the call. Use the complete 56-byte source range for
reproduction; the shorter range ends inside a call. The event label alone
does not establish an event identity.

<a id="r-unassigned-receiver"></a>
## Continue the unassigned receiver prologue

**Status:** Open.

**Start from:** the [five-byte prologue](firmware/UNASSIGNED.md#receiver-prologue).

**Useful result:** authenticate a caller or table edge selecting the anchor,
then follow the body from `0x6edc1109` (source `0x007bfce9`) to a bounded
consumer with argument definitions and call effects. Repeating the prologue
decode does not establish a stock receiver or image path.

## Maintaining questions

Use stable descriptive IDs in links. Update the existing question when accepted
evidence narrows it, and close it with a link to the resulting finding when it
is answered. Keep the question and its status here, with its established facts in the topic
reference. Use Answered only when the linked result settles the stated scope;
retain the ID and a short answer link instead of deleting the question. Follow [the maintainer rules](MAINTAINING.md#documentation-updates).

<details>
<summary>Links from earlier versions of this page</summary>

<a id="how-to-use-the-addresses-on-this-page"></a>

[How to use the addresses on this page](firmware/READING.md#coordinates)

<a id="good-first-contribution-extend-instruction-coverage"></a>

[Good first contribution: extend instruction coverage](#r-first-contribution)

<a id="resolve-the-release-control-candidates-indirect-consumers"></a>

[Resolve the release-control candidate's indirect consumers](#r-release-contract)

<a id="resolve-the-candidate-receiver-method-beyond-its-prologue"></a>

[Resolve the candidate receiver method beyond its prologue](#r-unassigned-receiver)

<a id="connect-the-initializer-to-the-selected-runtime-record"></a>

[Connect the initializer to the selected runtime record](#r-throughimage-record)

<a id="map-decoded-offsets-to-runtime-addresses"></a>

[Map decoded offsets to runtime addresses](#r-address-mapping)

<a id="recover-the-boot-entry-and-initialization-chain"></a>

[Recover the boot-entry and initialization chain](#r-startup)

<a id="continue-the-resolved-still-corridor-dispatch"></a>

[Continue the resolved still-corridor dispatch](#r-still-list)

<a id="resolve-the-throughimage-selectors-runtime-record"></a>

[Resolve the ThroughImage selector's runtime record](#r-throughimage-record)

<a id="resolve-a-read-only-ptp-request-and-response-lifecycle"></a>

[Resolve a read-only PTP request and response lifecycle](firmware/PTP.md)

<a id="identify-decoded-block-4s-external-owner"></a>

[Identify decoded block 4's external owner](#r-block-4)

<a id="external-evidence-wanted-integrity-and-authentication"></a>

[External evidence wanted: integrity and authentication](#r-integrity)

<a id="maintaining-this-page"></a>

[Maintaining this page](MAINTAINING.md#documentation-updates)

</details>
