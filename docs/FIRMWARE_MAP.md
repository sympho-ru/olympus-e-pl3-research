# Olympus E-PL3 firmware map

This is the reviewed guide to the Olympus E-PL3 Body 1.6 firmware. It explains
what the evidence supports and where to look next. The canonical source
coordinates, slice hashes, and instruction text remain in
[`ranges.jsonl`](../evidence/ranges.jsonl) and
[`instructions.jsonl`](../evidence/instructions.jsonl).

Start here for an overview, open a topic for exact relationships, or choose an
[open research question](RESEARCH.md). Before interpreting an address, read
[the coordinate and evidence conventions](firmware/READING.md).

<a id="observed-capabilities"></a>
## What has been observed on hardware?

Historical observations complement the static firmware reference. They describe
specific images, sessions, and host conditions; they do not identify every
internal implementation or establish the complete capture path.

| Capability or constraint | Observed result | Remaining limit |
|---|---|---|
| [Modified-image deployment](observations/DEPLOYMENT.md#modified-image) | An exact modified Body-1.6 image booted and returned its changed data marker | Arbitrary executable-patch safety and the validation mechanism |
| [Operation advertisement and dispatch](observations/DEPLOYMENT.md#advertisement) | Advertisement changed, but the tested capture and proxy requests were rejected | Actual live handler admission and selection |
| [Existing-image retrieval](observations/USB_AND_MEDIA.md#retrieval) | A selected JPEG was downloaded and its saved hash verified | Initiating capture and associating its new image with retrieval |
| [USB personalities](observations/USB_AND_MEDIA.md#personalities) | Storage and MTP/Print worked with different session and media behavior | Shooting-state interaction and runtime firmware connections |
| [Boot failure and recovery](observations/DEPLOYMENT.md#recovery) | One executable-table experiment failed to boot; one official-image recovery was reported | Exact fault mechanism and general recovery guarantees |

Source-record identities, measured versus user-attested steps, and public
reproducibility limits accompany the observations. Early USB records without
an exact image identity are not automatically Body-1.6-specific evidence.

## What is in the firmware?

| Decoded block | Current understanding | Missing connection |
|---:|---|---|
| 0 | Reviewed MN103 code includes startup, object lifecycles, candidate release control, and PTP-adjacent records/dispatch | Complete runtime placement and the connections between these areas |
| 1 | Record-indexed data images, localization resources, and materialization requests | The delegated service's effect and resource consumers |
| 2 | A bounded payload and a related parameter path | Its encoding and actual code consumer |
| 3 | Eight prefixed JPEG resources with an index | Index meaning and runtime use |
| 4 | A big-endian H8-compatible image with internal materialization | Consistent instruction interpretation, external loader, and hardware owner |

See [block layouts and container integrity](firmware/BLOCKS.md) for exact
structures and their qualifications. Block 3's bundled resources are not
evidence of newly captured images.

<a id="established-regions"></a>
## Browse the reviewed findings

| Topic | What the current evidence explains |
|---|---|
| [Startup](firmware/STARTUP.md) | Shared state words and a local overlay handoff; reset ownership is unresolved |
| [Release-control candidates](firmware/RELEASE_CONTROL.md) | Release and guarded action callers, bit-state guards, carrier methods, caller record writes, construction owner joins, receiver selection, conditional endpoint/native inputs and gate-clear receiver arguments, six-input frontend, and bounded selector-to-key lookups |
| [Still-corridor objects](firmware/STILL_OBJECTS.md) | Singleton dispatch, list population, separate object tables, [native still-request](firmware/STILL_OBJECTS.md#native-still-request) and [still-take](firmware/STILL_OBJECTS.md#native-still-take) boundaries, and field getter/setter relationships |
| [Live view and ThroughImage](firmware/LIVE_VIEW.md) | Object lifecycle, collection operations, and a selector returning a scalar through a record lookup |
| [PTP-adjacent records and dispatch](firmware/PTP.md) | Registration callers, FIFO mechanics, selectors, callbacks, descriptors, queued storage, a [qualified USB-state reporting wrapper](firmware/PTP.md#usb-state-wrapper), [conditional connection-candidate byte stores and consumer](firmware/PTP.md#usb-connect-stores), and a [named MTP lifecycle with a receive-record/pump join](firmware/PTP.md#mtp-communication-lifecycle) |
| [Decoded blocks and integrity](firmware/BLOCKS.md) | Data layouts, materialization requests, and the host parser's checksum boundary |
| [Unassigned source anchors](firmware/UNASSIGNED.md) | A complete caller slice and a receiver prologue without established subsystem ownership |

These are research-area names. For example, the release-control and live-view
labels do not establish capture or frame ownership. Each topic records the
particular missing connection beside the finding.

<a id="request-to-image"></a>
## How does this relate to host-controlled capture?

The practical target is one host command causing one still image and transfer
of that image to the host without physical interaction. The complete path is
not established. Each connection below needs its own evidence; the available
findings do not yet form an end-to-end route.

The [existing-image download](observations/USB_AND_MEDIA.md#retrieval) is an
observed capability available for reuse. The table below concerns the missing
connections to a host-initiated new capture and their static implementation;
it does not mean that basic USB communication or downloading is unproved.

| Required connection | Available static starting point | What remains to be proved |
|---|---|---|
| Receive a host request | [Registration callers and record handling](firmware/PTP.md#registration) | An authenticated transport receive path and selected request owner |
| Select a controllable handler | [Release frontend and callers](firmware/RELEASE_CONTROL.md), [constructed service dispatch](firmware/RELEASE_CONTROL.md#constructed-service) | The applicable receiver, method, input contract, preservation, and host connection |
| Initiate a still capture | [Release body](firmware/RELEASE_CONTROL.md#release-body), [guarded action](firmware/RELEASE_CONTROL.md#guarded-action), and [native still-take boundary](firmware/STILL_OBJECTS.md#native-still-take) | A source-supported capture effect beyond checks, labels, and direct or indirect calls |
| Identify the resulting image | [Caller-record writes](firmware/RELEASE_CONTROL.md#caller-record), [object consumers](firmware/STILL_OBJECTS.md#field-100), and [owner fields](firmware/PTP.md#descriptor-owner) | A concrete image/payload, its owner, and lifetime; record writes alone do not identify it |
| Transfer it to the host | [Reply packing and queued storage](firmware/PTP.md#reply-storage) | The image-to-transport connection and host completion |

An unresolved connection is not a disproved connection. Coverage counts and
static helper calls do not measure completion of this target. Research questions
and the evidence needed to resolve them are in [RESEARCH.md](RESEARCH.md).

<a id="current-coverage"></a>
## Canonical coverage

| Block | Authenticated ranges | Canonical instruction rows |
|---:|---:|---:|
| 0 | 13,101 | 53,298 |
| 1 | 827 | 0 |
| 2 | 4 | 0 |
| 3 | 35 | 0 |
| 4 | 3,230 | 0 |

Coverage is partial and non-contiguous except that the ranges cover all 65,536
bytes of block 4. Counts are checked against the canonical files; they are not
counts of functions or runtime paths. Block 4 has no canonical instructions
because conflicting H8 decodes remain unresolved. Historical instruction rows
are not certified by today's [contextual decode gate](DECODING.md).

## Reproduce or contribute

- [Obtain and verify Body 1.6](OBTAINING_FIRMWARE.md), then follow the [analysis workflow](ANALYSIS.md).
- Read [evidence formats](EVIDENCE.md) and [instruction verification](DECODING.md) to interpret a finding's support.
- Choose an [open question](RESEARCH.md) and follow [the contributor workflow](../CONTRIBUTING.md).
- Maintainers use [the acceptance and documentation rules](MAINTAINING.md).

<details>
<summary>Links from earlier versions of this page</summary>

<a id="startup-state-access"></a>

[Startup-state access](firmware/STARTUP.md#state-access)

<a id="bounded-caller-source-coverage"></a>

[Bounded caller source coverage](firmware/UNASSIGNED.md#complete-caller)

<a id="still-corridor-singleton-dispatch"></a>

[Still-corridor singleton dispatch](firmware/STILL_OBJECTS.md#singleton)

<a id="release-control-candidate-and-caller-profiles"></a>

[Release-control candidate and caller profiles](firmware/RELEASE_CONTROL.md#release-body)

<a id="six-input-frontend-and-control-object-accessor"></a>

[Six-input frontend and control-object accessor](firmware/RELEASE_CONTROL.md#six-input-frontend)

<a id="release-key-conversion-owner-candidate"></a>

[Release key-conversion owner candidate](firmware/RELEASE_CONTROL.md#key-conversion-owner)

<a id="live-view-object-lifecycle"></a>

[Live-view object lifecycle](firmware/LIVE_VIEW.md#lifecycle)

<a id="candidate-receiver-method-prologue"></a>

[Candidate receiver method prologue](firmware/UNASSIGNED.md#receiver-prologue)

<a id="throughimage-receiver-and-selector-scalar"></a>

[ThroughImage receiver and selector scalar](firmware/LIVE_VIEW.md#throughimage)

<a id="ptp-adjacent-registration-caller-source"></a>

[PTP-adjacent registration caller source](firmware/PTP.md#registration)

<a id="established-ptp-adjacent-record-initialization"></a>

[Established PTP-adjacent record initialization](firmware/PTP.md#fifo)

<a id="decoded-block-1-materialization"></a>

[Decoded block 1 materialization](firmware/BLOCKS.md#block-1)

<a id="decoded-block-2-boundary"></a>

[Decoded block 2 boundary](firmware/BLOCKS.md#block-2)

<a id="decoded-block-3-resource-bundle"></a>

[Decoded block 3 resource bundle](firmware/BLOCKS.md#block-3)

<a id="decoded-block-4-classification"></a>

[Decoded block 4 classification](firmware/BLOCKS.md#block-4)

<a id="host-visible-container-integrity"></a>

[Host-visible container integrity](firmware/BLOCKS.md#container-integrity)

</details>
