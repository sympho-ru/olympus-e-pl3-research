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

## Choose a starting point

| Interest | Questions |
|---|---|
| First contribution | [Extend a supported boundary](#r-first-contribution) |
| Release interface and inputs | [Release and guarded action](#r-release-contract), [caller record](#r-caller-record), [frontend inputs](#r-release-inputs), [key owner](#r-key-owner) |
| Still-object ownership | [List consumer](#r-still-list), [nested receiver](#r-still-receiver), [field +100](#r-still-field-100) |
| Live view and scalar records | [Frame owner](#r-live-view-owner), [ThroughImage record](#r-throughimage-record) |
| PTP-adjacent ingress and dispatch | [Registration](#r-ptp-registration), [request owner](#r-ptp-ingress), [vectors](#r-ptp-vectors), [status callbacks](#r-ptp-status), [handler banks](#r-ptp-handler-banks) |
| Storage and unjoined objects | [Queued storage](#r-ptp-storage), [descriptor consumer](#r-descriptor-consumer), [callback provider](#r-callback-provider), [descriptor tables](#r-ptp-descriptor-tables), [entry edges](#r-ptp-entry-edges) |
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

**Start from:** the [release body and caller profiles](firmware/RELEASE_CONTROL.md#release-body)
and [guarded action and carrier calls](firmware/RELEASE_CONTROL.md#guarded-action).
Also inspect the distinct [constructed service dispatch](firmware/RELEASE_CONTROL.md#constructed-service).

**Question:** which concrete receivers and input profiles reach the conditional
lookups, the helper at `0x6ebd9652`, and the action's dynamic methods reached
through source `0x0059a13c`?

**Useful result:** trace arguments and register preservation through the selected
calls to a bounded consumer or a capture/payload effect. Preserve the distinction
between range coverage and the sparsely recorded caller instructions. A status
return alone does not identify an image-producing operation. For the guarded
action, resolve preservation and object identity across slots `+16`, `+140`,
`+144`, `+20`, and `+148`; keep the saved carrier distinct from the receiver
returned by slot `+16`. Establish the pointer contract at writer source
`0x0059a7a1`: the construction branch guards an earlier call, not this writer.
For the constructed service, establish the cached root's validity and lifetime,
the concrete receiver selected from the `+1868` subobject's current field `+140`,
and its table's `+4` consumer. Verify `d2` preservation through selector slot
`+156` before equating the forwarded scalar with the incoming request. Resolve
the field's later value through helper and indirect storage effects: on the
qualified construction path, the initial `+140`/`+144` zero-write owner is
joined to the outer-base return and the `0x6eef8af8` installation, but zero is
not proved to survive those effects or live invocation. The root-return/cache
STORE identity is established only on the qualified valid nonzero normally
returning path; relate the later cache reload to that stored root through the
aggregate's global-state effects and establish validity/lifetime. The final
`+1868` constructor return and remaining pointed-storage/register contracts
are separate from those partial joins.
Root wiring's `+272`/`+276`/`+160` writes are distinct from that field. The
selected bodies do not establish an exhaustive producer census. Keep this
service distinct from the guarded action's carrier until a source-supported
join is established.

<a id="r-caller-record"></a>
## Identify the caller record's owner and consumers

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

**Start from:** the [six-input frontend](firmware/RELEASE_CONTROL.md#six-input-frontend).

**Question:** what is written on conversion failure, and which concrete method
does the returned control object's slot `+304` select?

**Useful result:** establish destination initializedness, the installed table's
data mapping, receiver readiness, and the selected method's consumer. Keep six
current destination words distinct from six successfully parsed inputs; the
frontend's normal zero return is not a capture-success result.

<a id="r-key-owner"></a>
## Connect the candidate key-conversion owner

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

**Start from:** [singleton dispatch and population](firmware/STILL_OBJECTS.md#singleton).

**Question:** what is the list's runtime class, and which object receives the
later slot-`+20` call?

**Useful result:** a supported producer/consumer connection from the populated
list to that dispatch. Object creation and list append do not establish exposure
or image production.

<a id="r-still-receiver"></a>
## Identify the nested receiver of the +2216 object

**Start from:** the [separate object path](firmware/STILL_OBJECTS.md#owner-2216),
especially the nested call at `0x6ee1d52a`.

**Useful result:** establish the concrete receiver/table and the returned field's
producer or consumer, then test whether it joins the singleton corridor. Preserve
the getter's distinct local and canonical load-address anchors.

<a id="r-still-field-100"></a>
## Trace the pointer stored in field +100

**Start from:** the [getter, writer, and separate table candidate](firmware/STILL_OBJECTS.md#field-100)
and their [dispatch continuations](firmware/STILL_OBJECTS.md#continuations).

**Question:** who supplies the setter's incoming pointer, and which concrete
parent and returned object reach the slot-`+8`/`+48` consumers?

**Useful result:** prove those identities through the calls. Keep the parent
saved in `a2`, other incoming object in `d3`, and getter result in `a3` distinct.
Shared methods do not select a parent table; one table's slot-`+40` no-op does
not resolve the other object's call at `0x6ee1db91`.

<a id="r-live-view-owner"></a>
## Identify the live-view frame owner

**Start from:** the [collection and copy paths](firmware/LIVE_VIEW.md#collections).

**Useful result:** identify the helper's caller-supplied object or the destination
of the three-word copy, then connect it to `outer+132` or a concrete frame handle
and consumer. Previous exact string-address scans did not find an
instruction-aligned owner reference; another vocabulary scan alone is unlikely
to answer the question.

<a id="r-throughimage-record"></a>
## Find the producer of the ThroughImage record

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

**Start from:** the [registration callers and builder](firmware/PTP.md#registration).

**Useful result:** establish this module's source-to-runtime placement and bind
the callback literals to authenticated entries. Separately establish whether
caller metadata 2 survives the allocator's transitive calls in `d3` to node
`+2`. The singleton module's delta is insufficient for this module.

<a id="r-ptp-ingress"></a>
## Connect the primary request owner to ingress

**Start from:** the [primary selector's caller](firmware/PTP.md#request-selector)
and [FIFO](firmware/PTP.md#fifo).

**Useful result:** identify the stack-record owner's relationship to a transport
receive boundary and the known FIFO. The `0x6e6860f7` contract on the bit-1-set
path is a bounded subquestion. Record layout and the shared descriptor handoff
alone do not establish live admission or wire completion.

<a id="r-ptp-vectors"></a>
## Establish selector-vector placement and entry

**Start from:** the [neighboring vectors](firmware/PTP.md#selector-vectors).

**Useful result:** establish source placement and the caller/owner supplying
`0x5001` to `0x6f33362c`. Keep the two runtime bases and neighboring interior
targets distinct. A vector does not establish a common entry ABI.

<a id="r-ptp-status"></a>
## Resolve status callbacks and the skipped interior entry

**Start from:** [status dispatch and callback installation](firmware/PTP.md#status-callbacks).

**Useful result:** identify the initializer's runtime owner/order, the writer
of `0x60355a2c`, the callback contract through `0xa07b702c`, or a consumer of
`0xa07b7030`. To connect the `0x5001` dispatcher, supply an authenticated
predecessor selecting `0x6f33aaad`; the installed entry at `0x6f33aa63` skips it.

<a id="r-ptp-handler-banks"></a>
## Identify the handler-bank producer and selection

**Start from:** the [paired writers and complete callers](firmware/PTP.md#handler-banks)
and the [callback record route](firmware/PTP.md#callback-body).

**Useful result:** trace the callers' incoming `a1` and prove or rule out its
base being `0x6f358d30`. Establish the executable handler value and the runtime
selection of `0x6f330b53` before claiming a live handler. Field geometry and
the fixed consumer's register route are insufficient without that connection.

<a id="r-ptp-storage"></a>
## Identify queued storage and its consumer

**Start from:** the [reply and storage corridor](firmware/PTP.md#reply-storage).

**Useful result:** identify the concrete object selected by `(d0 & 0x7000) >> 12`,
its queue allocation, and the caller of the source-only writer at `0x000a9736`,
including the object supplied in `a1`. Then establish the storage consumer.
A copied reply buffer does not establish USB submission or wire completion.

<a id="r-descriptor-consumer"></a>
## Find the descriptor owner's output consumer

**Start from:** the [owner-state operations](firmware/PTP.md#descriptor-owner).

**Useful result:** authenticate a consumer of owner `+112/+116/+120` and result
halfword `+124`, tracing required state and helper outcomes from the caller.
Keep outer `+0` and nested `+2` switches distinct; a later outer-2 invocation
may inherit outer-1 state. Identify payload type and lifetime before calling
the result an image or file.

<a id="r-callback-provider"></a>
## Resolve the separate callback provider

**Start from:** the [callback object family](firmware/PTP.md#callback-objects).

**Useful result:** resolve the writer/value of `P+0x20`, the parent field's
producer or source class, or same-object writers of `O+0xac` and `O+0xf4`.
The factory calls the pointer stored directly at `P+0x20`; an extra dispatch-table
dereference is unsupported. A connection to a known selector, queue, or transport
owner also needs independent evidence.

<a id="r-ptp-descriptor-tables"></a>
## Find consumers of the unjoined descriptor tables

**Start from:** the [17-record and 66-record tables](firmware/PTP.md#descriptor-tables).

**Useful result:** identify the runtime owner and selection of the 17-record
table, including whether it selects `0x100e`, and resolve slot `+20` of the
object reached from `d2+24`. For the separate key-`0x4e` table, establish its
runtime placement, key selection, and indirect invocation. The neighboring
lookup families and raw alignment false positives do not supply those edges.

<a id="r-ptp-entry-edges"></a>
## Establish entry edges for isolated handlers and alternate starts

**Start from:** the [handler and byte-gap starts](firmware/PTP.md#unselected-entries)
and [current decode boundaries](firmware/PTP.md#decode-boundaries).

**Useful result:** identify the late handler's producer/runtime owner or a
supported caller/table edge selecting an alternate start. Complete instruction
widths and independently reproducible overlapping decodes do not prove entry.

<a id="r-address-mapping"></a>
## Establish a local address mapping

**Start from:** the [coordinate conventions and examples](firmware/READING.md#coordinates).

**Useful result:** authenticate a relationship between decoded offsets, copied
regions, overlays, or runtime addresses, or bound why competing views remain.
An arithmetic match without a supported caller, table, or relocation context
is not placement evidence.

<a id="r-startup"></a>
## Connect the startup chain to reset

**Start from:** the [state accesses](firmware/STARTUP.md#state-access) and
[local overlay handoff](firmware/STARTUP.md#overlay-handoff).

**Useful result:** authenticate a predecessor, initialization owner, task
boundary, or runtime-built pointer connecting the handoff to reset. The bounded
block-0 direct/literal census is already negative; repeat it only with a new
reason it would answer the missing connection.

<a id="r-block-1"></a>
## Resolve block 1's delegated materializer

**Start from:** [block 1's record and request layout](firmware/BLOCKS.md#block-1).

**Useful result:** independently anchor the complete caller context, select the
applicable address view, and follow the service below `0x402e90bc` to a payload
effect that distinguishes copying, DMA, or address mapping. Preserve record 0's
`a3 == 0` condition. Broad structural rescans alone do not identify a consumer.

<a id="r-block-2"></a>
## Find block 2's consumer

**Start from:** [block 2's boundaries and parameter path](firmware/BLOCKS.md#block-2).

**Useful result:** follow the delegated boundary to a payload read, copy,
mapping, or consumer effect. The equality between base-plus-length and a header
word is insufficient. Prior text, packing, compression/transform, cross-block
copy, and canonical-operand searches did not identify a consumer.

<a id="r-block-3"></a>
## Find the block 3 resource consumer

**Start from:** the [JPEG bundle](firmware/BLOCKS.md#block-3).

**Useful result:** connect an index entry or 16-byte record prefix to an
authenticated block-0 read, copy, decode, or display path. Exact extents and
dimensions are established; visual similarity does not establish a UI role.

<a id="r-block-4"></a>
## Resolve block 4's decoder and external owner

**Start from:** the [H8-compatible image](firmware/BLOCKS.md#block-4).

**Useful result:** reproduce the common target at offset `0x122a` with an
independently supported H8 decode, then trace the producer of selector
`0x004003c1`. Investigate whether the block-0 context at `0x00338a80` leads to
a fifth-body descriptor, transfer, or start. The shared literal alone supplies
no such connection, and no block-4 instruction row is canonical.

<a id="r-integrity"></a>
## Establish updater or device authentication

**Start from:** the [host-visible container result](firmware/BLOCKS.md#container-integrity).

**Useful result:** independently inspect a verifier, updater/device validation
path, technical documentation, or reproducible static artifact. Host parser
acceptance of a repaired checksum does not establish device acceptance; product
pages, filenames, and requester-side access controls do not answer this question.

<a id="r-unassigned-caller"></a>
## Establish the unassigned caller's context

**Start from:** the [complete caller span](firmware/UNASSIGNED.md#complete-caller).

**Useful result:** establish an authenticated entry/caller and argument
preservation through the call. Use the complete 56-byte source range for
reproduction; the shorter range ends inside a call. The event label alone
does not establish an event identity.

<a id="r-unassigned-receiver"></a>
## Continue the unassigned receiver prologue

**Start from:** the [five-byte prologue](firmware/UNASSIGNED.md#receiver-prologue).

**Useful result:** authenticate a caller or table edge selecting the anchor,
then follow the body from `0x6edc1109` (source `0x007bfce9`) to a bounded
consumer with argument definitions and call effects. Repeating the prologue
decode does not establish a stock receiver or image path.

## Maintaining questions

Use stable descriptive IDs in links. Update the existing question when accepted
evidence narrows it, and close it with a link to the resulting finding when it
is answered. Keep the substantive question in this file and its established
facts in the topic reference. Follow [the maintainer rules](MAINTAINING.md#documentation-updates).

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
