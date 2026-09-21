# Observed USB, media access, and capture limits

[Map](../FIRMWARE_MAP.md) · [Deployment experiments](DEPLOYMENT.md) ·
[Evidence conventions](../firmware/READING.md#evidence-and-claims)

The E-PL3 has provided working host access to existing photographs. Producing
a new photograph through a host command, then identifying and retrieving that
particular result, remains unproved. The observations here describe individual
historical sessions; they are not a statement about a currently connected
camera or a complete firmware implementation map.

- [USB personalities and session ownership](#personalities)
- [Existing-image retrieval](#retrieval)
- [Movie access](#movies)
- [Capture and live-view limits](#capture-limits)
- [What still needs validation](#remaining-validation)
- [Source identities](#sources)

The July 9–10 records below do not bind every run to an exact body firmware
image or complete host/tool version. They must not silently be treated as
Body-1.6-specific results. A DeviceInfo version such as `1.00` is not a verified
camera-menu firmware version. The later [modified-image experiments](DEPLOYMENT.md)
provide separate candidate and official-parent identities.

<a id="personalities"></a>
## USB personalities and session ownership

Historical macOS observations distinguish Storage (`07b4:012c`, mass storage)
from MTP/Print (`07b4:0113`, still-imaging/PTP). The shared USB identity does
not make MTP and Print interchangeable. The retained summary and Storage import
report identify the personalities; the [marked redirect trial](DEPLOYMENT.md#redirects) records their different
DeviceInfo payload lengths and session behavior (U1, U3, and
[D4](DEPLOYMENT.md#sources)).

In the tested Print session, a PictBridge printer exchange, including
`configurePrintService`, succeeded before session close. The corresponding
MTP observation established an ordinary PTP session separately. Initial
interface-claim failures involved competing macOS camera clients. Such a
failure is a host-ownership result; it is not proof of a boot failure or a
camera command rejection. These are diagnostic conditions to preserve when
comparing experiments, not instructions to change host service ownership.

<a id="retrieval"></a>
## Existing-image retrieval

On 2026-07-09, a selective MTP import enumerated metadata for existing JPEGs
and downloaded one selected object. The saved result reports two candidates,
one selection, one completed download, and status `downloaded_selected` (U2).

| Measurement | Observed value |
|---|---|
| Selected object handle | `0x00000003` |
| Object size | 1,954,962 bytes |
| Saved download SHA-256 | `e9eaf7a9d4208f0a12dee680ee6a0131c072f9ac9e7e9bc916fd9f765059a2e8` |
| Metadata operations | `OpenSession`, `GetStorageIDs`, `GetObjectHandles`, `GetObjectInfo`, `CloseSession` |
| Selected transfer | `GetObject` |

The retained downloaded file's size and SHA-256 match that result. This
establishes retrieval of an existing photograph in the tested session. It does
not establish how to initiate a new capture, that a previously used handle
remains stable, or which event or polling result identifies a newly created
object. The same historical work records metadata/status, thumbnail, and
selective-import capabilities (U1); the exact download above is the concrete
reproduction anchor retained here.

The host can reuse this retrieval capability if a capture path produces an
accessible stored object. The firmware's [queued storage corridor](../firmware/PTP.md#reply-storage)
has not thereby been identified as the implementation of that capability.

<a id="movies"></a>
## Movie access differs from JPEG access

The July 10 MTP media scout recorded five visible objects: two folders and
three JPEGs, with no movie objects and no fallback metadata (U4). A later
Storage-mode import obtained a user-confirmed playable AVCHD movie from the
card. The import manifest records a 14,389,248-byte original with SHA-256
`d2f7e843f166e9f5fa40114b66a67ae9744ddfed685b0dda86b400c0ed3d7db7` (U3, U5).
Saved stream metadata reports a 6.528-second H.264/AC-3 stream (U6). The retained
decode log is empty (U7): it contains no diagnostic text. An empty log alone
does not establish that decoding ran or completed successfully; the separate
user confirmation above records playability.

This establishes a Storage/card route for that movie and the narrower contents
of the tested MTP view. It does not establish that every movie format is
inaccessible through every PTP operation, or that the host triggered movie
recording. Media-format advertisements alone do not establish object visibility.

<a id="capture-limits"></a>
## Capture and live-view limits

The July 9 host capture trial returned unsupported-operation errors for
gphoto2 trigger, image-capture, and preview actions (U8–U10). Those messages
establish failure of the tested host-tool route. In particular, a host error
does not prove that an exact PTP capture request reached the camera.

A stronger, separately identified observation is the later
[advertised capture-request trial](DEPLOYMENT.md#advertisement): on a known modified image,
one `InitiateCapture(0,0)` request received camera response `0x2005`. It must
not be relabeled as a test of stock firmware. The separate object-handle proxy failure
also does not prove that all possible capture routes are unavailable.

The July 9 video scout found no real video input in the host's AVFoundation
enumeration while the E-PL3 was USB-visible; it did not open a stream (U11).
That bounded host enumeration does not establish the absence of every
possible live-view interface. Serving an imported JPEG as a latest-still page
or an MJPEG wrapper does not turn it into live sensor video.

The capture/import runner's July 9 report explicitly records
`real_actions_executed: false`, `new_media_detected: false`, and
`unattended_actual_capture_now: false` (U12). Its trigger was a software
rehearsal. A ready runner, simulated remote release, or successful import is
not proof of a new physical exposure. Simultaneous remote release and USB
import, automatic return to MTP after reconnection, and a fully unattended
capture cycle were not established by that rehearsal.

<a id="remaining-validation"></a>
## What still needs validation

The existing records suffice to retain the deployment and retrieval baseline;
those facts do not require repeating a flash or generic capture sweep.
Different questions remain:

- [Live request ownership and handler selection](../RESEARCH.md#r-ptp-ingress):
  bind a received host operation to the actual firmware path, using known
  working read operations and retained transactions as controls.
- [Capture effect and valid receiver/input state](../RESEARCH.md#r-release-contract):
  establish that the candidate path produces an image under the relevant state.
- [USB shooting-state interaction](../RESEARCH.md#r-usb-shooting-state):
  distinguish camera-mode restrictions from session and interface ownership.
- [New-object identification and retrieval](../RESEARCH.md#r-capture-retrieval):
  connect a particular initiated capture to its newly accessible image and
  successful host download.

These are research questions, not scheduled jobs or camera-operation authority.
Historical firmware identity and host-version gaps should first be checked
against the retained acquisition records. If they cannot be recovered, keep
the observation's applicability qualified; do not invent missing metadata or
require a new experiment merely to remove an honest historical limitation.

<a id="sources"></a>
## Source identities

These IDs bind private source records used for the authored summaries above.
The maintainer retains their path mapping. Raw captures, personal media,
device identifiers, and host paths are withheld. A digest binds file contents,
not the truth of a measurement; public readers can inspect the summarized
conditions and outcomes but cannot independently replay the withheld records.
The observation classes and verification limits also apply to
[deployment evidence](DEPLOYMENT.md#sources).

| ID | Retained record | SHA-256 |
|---|---|---|
| U1 | Historical USB and media summary | `635920b6756f439d394ae14bda1bb2aba1e4f62891fd9506de4816165eacce84` |
| U2 | Selective JPEG import result | `dc7c411d4d99d7d9717b6e43350da7a26b1f9a0812d346abce0e3fb26a8a4aa3` |
| U3 | Storage movie import report | `46b4b640fbfc7be335f6e946633262f4d8a2d09d619c659ad9784a1c199c2560` |
| U4 | MTP media scout report | `5b882bf7af38de125623c23b77a7c0609cc69057c01d7e04541b51fb3ed27e23` |
| U5 | Storage import manifest | `1fa4b0b67c744d28adef4690112ec701672697b3dbf61c58d3745304ae2468a9` |
| U6 | Movie stream metadata | `f11c6b13d1663c34256352673f56d8e76e4abcc1c02017870f4002ae58b42da5` |
| U7 | Original movie decode log (empty file; no diagnostic text) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| U8 | Host trigger-capture error | `220b2a4ac24ab4264936e3e90000b57078b169011ba40533a026d45db0b6d139` |
| U9 | Host capture-image error | `a99d86bb7edd64021e0c0195cc13c8ac7c903e4149492385a3c71d03d88e383e` |
| U10 | Host capture-preview error | `df618d7e17f3ae8a4f0dec812414d7ca3a6a0ee8288c2b91ffe407ddfe216930` |
| U11 | Host video-input scout report | `c7bcd8730578203023ef2367202fb358e4f91822ff29b4135cd23b65256324ff` |
| U12 | Capture/import rehearsal report | `511174bbe02cb0b088c5f82904dc8f30828c1f87a748be36d1b76eb58c1cdb8b` |
