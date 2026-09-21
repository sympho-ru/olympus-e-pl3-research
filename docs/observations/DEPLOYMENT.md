# Observed firmware deployment and handler experiments

[Map](../FIRMWARE_MAP.md) · [USB and media](USB_AND_MEDIA.md) ·
[Evidence conventions](../firmware/READING.md#evidence-and-claims)

Specific modified E-PL3 images were transferred, booted, and their data changes
observed over PTP. Executing the intended handler change is a separate problem:
the tested redirects failed, and a later executable-table change prevented
normal boot. These historical observations establish more than a host-parser
test, but do not establish general executable-patch safety.

- [Modified image active after boot](#modified-image)
- [Direct-call redirects and session controls](#redirects)
- [Advertisement and actual operation acceptance](#advertisement)
- [Boot failure and one recovery](#recovery)
- [Source identities and verification limits](#sources)

The source records use local labels such as `EXP-001`. These are aliases from
one historical series, not a numbering system contributors must adopt. The
readable names below describe the purpose; the alias only connects to retained
records. See [how to name and submit an observation](README.md).

| Readable name | Historical alias |
|---|---|
| Data-marker activation after reboot | `EXP-001` |
| First StorageIDs redirect trial | `EXP-006` |
| Marked StorageIDs redirect trial | `EXP-007` |
| Advertisement and capture-request trial | `EXP-008` |
| Object-handle proxy trial | `EXP-009` |
| Executable-table boot-failure trial | `EXP-010` |

The experiments below used candidates derived from official Body 1.6, parent
SHA-256 `89b70dd65c6739de1cd762777205953ee15864df73369b84815df7ed8a0eb4b1`.
Candidate identities refer to the delivered artifacts, not firmware readback.
The host was macOS; these records do not establish portability to other hosts
or updater versions. They describe completed observations, not instructions
or authorization to repeat a transfer.

<a id="modified-image"></a>
## Modified image active after boot

On 2026-07-13, the data-only marker image in the activation trial (`EXP-001`)
completed the attended update
and returned DeviceInfo version `1.01` after power cycling into Print mode.
The host gate recorded `marker_confirmed`, a successful response, and matching
response transaction ID. The outcome also records the camera LCD completion
and the attended power cycle (sources D1–D2).

| Identity or measurement | Value |
|---|---|
| Candidate SHA-256 | `c892065b4a6f790c788d315eedd1297601786dd36be24f5521cce47e2df90ebb` |
| Candidate size | 46,596,160 bytes |
| Historical baseline DeviceInfo version | `1.00` |
| Observed DeviceInfo version | `1.01` |
| Marker source site | Block 0, offset `0x00d59706` |
| Containing canonical source range | Block 0, offset `0x00d596fb`, length 13 |

This establishes acceptance and post-boot use of this particular modified
image's data. It does not show an arbitrary instruction patch executing,
identify the device's validation mechanism, or prove capture support. The
DeviceInfo marker is not the body version displayed in the camera menu.

<a id="redirects"></a>
## Direct-call redirects and session controls

The first and marked redirect trials (`EXP-006` and `EXP-007`) intended to redirect `GetStorageIDs` (`0x1004`) to a
DeviceInfo response. The expected redirect was not observed (D3–D4).

| Experiment and date | Image and session evidence | Result and limit |
|---|---|---|
| First redirect trial, 2026-07-14 | Attended transfer reached user-reported LCD completion; subsequent Print session opened successfully | `0x1004` returned 8-byte ordinary StorageIDs data and `0x2001`; an active-image marker was not checked, leaving installation versus runtime-site ambiguity |
| Marked redirect trial, 2026-07-14–15 | Marker `1.03` was observed in both Print and MTP; valid sessions were separately established | Both personalities returned ordinary 8-byte StorageIDs data and `0x2001`, rejecting this exact redirect hypothesis even with the data marker active |

First redirect candidate SHA-256:
`33c63c8b48122148bbf205c55b47da20647668ffeb0c70a10949dff95ca0283a`.
Marked redirect candidate SHA-256:
`86ece3d8a9bbd34d8070310e512bfddbb2f744243cae135dc7be019c0c41b129`.

Earlier failed interface claims and an invalid Print OpenSession were not
tests of `0x1004`: the guarded collector did not send it. The later Print
observation completed a PictBridge printer exchange and returned the ordinary
storage ID `0x00010001`. MTP was tested separately. Print's marker payload was
167 bytes; MTP's was 171 bytes. Comparing one personality against the other's
payload caused a host validation mismatch, not an image-activation failure.

These results constrain the tested loaded-code/redirect hypotheses. They do
not disprove executable patching in general or establish that Print and MTP
share the same internal worker. See the [USB session observations](USB_AND_MEDIA.md#personalities).

<a id="advertisement"></a>
## Advertisement and actual operation acceptance

The advertisement/capture trial (`EXP-008`) changed the live MTP DeviceInfo operation list. On 2026-07-18, a
sessionless `GetDeviceInfo` returned 20 operations, with slot 10 advertising
`0x100e` in place of stock `0x100b`. Its DeviceInfo version remained `1.00`.
The source site is block 0 offset `0x00d59892`, within canonical range
`(0, 0x00d5987e, 33)`. This is an observed data-profile effect (D5).

Candidate SHA-256:
`48def97d30677cd696060c7f07611e721e2b86c07898eef61a6f2cae97832ab7`.

A separate one-shot session then tested `InitiateCapture(0,0)`. The object-handle proxy trial (`EXP-009`) used
a different image with marker `1.04` and the same advertised opcode to test a
read-only object-handle proxy (D6–D8).

| Observation | Preconditions | Exact tested request | Camera result |
|---|---|---|---|
| Advertised capture request | MTP profile matched; session opened; storage and object handles enumerated | One `0x100e`, parameters `[0, 0]` | Normally framed `0x2005 OperationNotSupported`; no new handles recorded and no image retrieved |
| Object-handle proxy request | MTP marker `1.04` and advertisement matched; session opened | One `0x100e`, parameters `[65537, 0, 0]` | `0x2005 OperationNotSupported`, zero data payload; session closed successfully |

Object-handle proxy candidate SHA-256:
`abc6a7b1843c1760d0507a9830473c8169c3fccab9e8e80d357563a46286e302`.

The proxy trial's parameters describe its intended proxy experiment, not a stock
capture recipe. Its result record identifies no retry. Together these
observations show that changing advertisement, and the particular static
route changes tested, did not activate the intended live handler. They do not
identify which firmware acceptance or dispatch check rejected the requests.
The [live ingress connection](../RESEARCH.md#r-ptp-ingress) remains unresolved.

<a id="recovery"></a>
## Boot failure and one recovery

On 2026-07-18, the executable-table boot-failure trial (`EXP-010`) reached the user-reported camera LCD completion state,
then failed to boot normally after power cycling. The incident record reports
no USB enumeration and no post-boot PTP request. Its candidate SHA-256 was
`72b16a809ea1260cdfa6b87f9ccab70e8a29708ef6d9f70ae68e7d24e14604b2` (D9).

The record attributes the failure with high confidence to an unproven
executable-table change. There was no crash trace or failed-image readback,
so the precise CPU fault and boot stage are not established. Successful
construction, delivery, and LCD completion did not establish boot safety.

The user subsequently reported a successful SD recovery using the official
Body 1.6 image, followed by normal boot and operation. The source image was
identified by the parent hash above. The record explicitly lacks a hash of
the file on the physical SD card and a post-recovery camera-menu version
reading. Recovery and normal operation are user-attested observations; this
is one recovery on this body, not evidence of a guaranteed rollback or
dual-bank mechanism.

That candidate was retired after this incident. Follow-up designs carrying
local aliases `EXP-011` through `EXP-016` were
revoked without physical testing; their existence is not experimental evidence.
The incident remains a constraint on interpreting deployment success, not a
reusable candidate or recovery procedure.

**Open questions:** [validation mechanism](../RESEARCH.md#r-integrity),
[live handler selection](../RESEARCH.md#r-ptp-ingress), and
[capture effect and valid inputs](../RESEARCH.md#r-release-contract).

<a id="sources"></a>
## Source identities and verification limits

The statements above are maintainer-reviewed summaries of retained historical
outcomes and selected host records. The source IDs below name those private
records; SHA-256 binds their exact contents. The public summaries omit raw
firmware, protocol dumps, device identifiers, host paths, and updater artifacts.
The maintainer retains the source mapping. Hashes do not authenticate a physical
event or make the withheld records publicly reproducible. User observations
remain distinguished from host measurements; no new hardware experiment was
performed to prepare this reference.

| ID | Retained record | SHA-256 |
|---|---|---|
| D1 | Data-marker trial: physical outcome | `ad0b95986945605699ecbf327920af0220374b5973e2d2138ee32cf099e47660` |
| D2 | Data-marker trial: post-boot host gate | `a80921ea0fcfa5dfe4adb74de6122e370b0d249e38060601a461d4b1576ccd8e` |
| D3 | First redirect: delivery and post-boot outcome | `3bb0599b0a8fab68bf46adf83ab50624d5fc28956ab371bd22bad33b41187e4c` |
| D4 | Marked redirect: marker and Print/MTP outcomes | `9fd50874d5bbed41b121818acc8248d2f49cddab0aa37033f2cb8a7f56d926ed` |
| D5 | Advertisement trial: transfer and profile outcome | `e3a18598b6c728f700b279295854934b2c3618a987128d68fd155a0609f7e9a2` |
| D6 | Advertised capture request: camera result | `0e319721f5ce3fed81e58596baa3ea4582bbf658b0e66ed6e0fe8aef61c17371` |
| D7 | Object-handle proxy: physical/proxy outcome | `0d2fce3e8b4875011addb3eca28f4263e59d0e72a9e26a993fb57842da0c577e` |
| D8 | Object-handle proxy: camera result | `0d106ab33d9888250691eec5848981f07b2ccdb4d04d9d3fcf03bfea4a0c590d` |
| D9 | Executable-table trial: incident and recovery outcome | `462e39bfb1bc54cef98192963e60110f7b0f9dc8c92819ec03cd1a93406a9b88` |
