# Reading the firmware references

[Map](../FIRMWARE_MAP.md) · [Open questions](../RESEARCH.md)

The references explain the current reviewed understanding of Body 1.6.
Canonical coordinates, hashes, and instruction text remain in
[`ranges.jsonl`](../../evidence/ranges.jsonl) and
[`instructions.jsonl`](../../evidence/instructions.jsonl). The references add
human-reviewed interpretations; they do not change either evidence schema.

<a id="evidence-and-claims"></a>
## Evidence and claims

| Term | What it establishes | Limit |
|---|---|---|
| Authenticated range | A block, offset, length, and SHA-256 identify source bytes | Coverage alone does not establish an instruction or behavior |
| Canonical instruction | A reviewed textual decode is recorded for an exact source slice and address anchor | Older rows are not certified by today's contextual gate; a decode does not prove entry or execution |
| Static relationship | Reviewed code or data supports a specific call, write, lookup, or local mapping | State, receiver identity, and intervening call effects still matter |
| Candidate or hypothesis | A proposed role, placement, or connection worth investigating | It must not be used as an established premise |
| Bounded negative | A stated search or path excludes a particular possibility | It does not exclude other blocks, address views, indirect paths, or runtime-built state |
| Host measurement | A retained host record reports a response, transfer, file, or other measured result | Host-tool failure is not necessarily a camera response; setup and image identity bound applicability |
| Hardware observation | A recorded physical experiment supports the stated behavior on the tested body/image | It does not prove the internal implementation, general patch safety, or behavior under other conditions |
| User attestation | The operator reports a physical step or visible result | It is distinct from a captured host measurement or firmware readback |
| External documentation | An identified source describes a product or interface | Model, revision, and applicability require review; it is not an observation of this body |
| Simulation or rehearsal | A model or host runner exercised a specified scenario | A simulated success does not establish camera actuation or image production |

These are different kinds of evidence, not steps on an automatic confidence
scale. A range-only contribution may support a reviewed structural finding; an
instruction row may still have an unresolved entry anchor. See [contextual
verification](../DECODING.md) for the mechanical gate and its limits.

Behavior in the firmware topic pages is static unless explicitly supported by
other evidence. The [observation pages](../FIRMWARE_MAP.md#observed-capabilities)
record historical hardware and host results separately, with source identities,
conditions, and limitations. Specific modified-image deployment and existing
JPEG retrieval have been observed; no complete host-request-to-new-image-transfer
path has been established. Capture, image ownership, and general patch safety
require their own evidence. Each entry retains the particular uncertainty that
limits its result, especially receiver identity and register preservation.

Private source-record hashes bind the retained artifacts but do not make a
physical event independently reproducible. Public observation summaries must
state what was measured, what was attested, and which supporting material is
withheld. Missing historical firmware or tool identity stays explicit. A
DeviceInfo version string is not automatically the camera-menu body version.

<a id="coordinates"></a>
## Source coordinates and address views

Use **block + offset + length** to locate a source span. Offsets are relative
to a decoded block, not the original container. Lengths are in bytes. A range
written `[start,end)` excludes `end`; `start..end` follows the endpoint
wording in that entry. Do not silently reinterpret old inclusive endpoints.

An instruction's JSON `address` is a decimal integer identifying its recorded
disassembly address; the docs normally render it in hexadecimal. A local
address view is the address assigned to a particular source window. Its
arithmetic does not by itself prove runtime placement. A runtime data address
such as `0xa07b81cc` is not a source offset.

| Example | Address | Block | Offset | Address minus offset |
|---|---|---:|---|---|
| Startup write | `0x402c02fb` | 0 | `0x0000031b` | `0x402bffe0` |
| PTP initializer | `0x6f330905` | 0 | `0x00d30925` | `0x6e5fffe0` |
| ThroughImage receiver | `0x6edfc227` | 0 | `0x007fae07` | `0x6e601420` |
| Separate object initializer | `0x6ec0b717` | 0 | `0x0060b2f7` | `0x6e600420` |
| Descriptor helper | `0x6e69d892` | 0 | `0x0009d892` | `0x6e600000` |

These examples define arithmetic for the cited anchors only. They are not a
module-wide mapping table. Code and data may need different corroboration; the
same displayed address can name different source windows. When two views
coexist, state both and explain which caller, table, or relocation relation
supports the one being used. Never derive a target from a global block-0 base.

Record-member offsets such as `+4` refer to the named object, not a block.
Matching offsets in two objects do not establish that they are the same object.
For a decisive path, retain compare operands, branch outcomes, argument
definitions, intervening calls, and the consuming instruction.

<a id="labels"></a>
## Research labels

| Label | Meaning in these docs |
|---|---|
| Startup | Early state access and initialization candidates; reset ownership is unresolved |
| Still corridor | Code around `0x4096368d` and related object dispatch; capture effect is unresolved |
| Release control | Candidate routines around `0x6ebc92d7` and frontend `0x6ebe36b0` |
| Live view | A mapped object lifecycle and collection path; frame ownership is unresolved |
| ThroughImage | The receiver/selector path from `0x6edfc227`; its returned scalar is not an identified image pointer |
| PTP-adjacent | Records and dispatch around `0x6f3307f5`, attributed from constants and local labels; host ingress is unresolved |
| Source vector at `0x00d58918` | The coordinate-based name used here for the vector called X3C in earlier notes; no semantic expansion is established |
| Unassigned caller / receiver | Source `0x006b0204` and prologue `0x007bfce4`; the earlier event-30 label does not establish an event or owner |

Names describe research areas, not recovered Olympus symbols or proven product
features. Prefer a descriptive name and exact anchor when a label's meaning is
unknown.

<a id="finding-format"></a>
## Finding format and evidence lookup

A topic page starts with a plain-language result and a local contents list.
Each stable section states its result and decisive limitation before the exact
support. Define object-role names within the finding; the same letter or field
offset in another finding does not establish identity. Use subheadings for
distinct mechanisms, tables for mappings/fields/branch outcomes, and prose for
control/data-flow reasoning. Link to the specific question in `RESEARCH.md`
instead of duplicating its investigation instructions.

Coordinate tables use separate **Block**, **Offset**, and **Length** columns.
By default these name exact canonical ranges; an explicit **Reference** value
of **Range** means the same thing. The canonical row supplies its hash. A range
is a selected entry point, not an assertion that all its instructions are canonical.

Use **Reference: Instruction span** with **Recorded address** for an extent
fully covered by canonical instruction rows in that address view, including a
single-instruction anchor. This does not require an artificial enclosing range
row. The check establishes coverage, not a callable function or execution path.
Describe sparse islands, contextual lookahead, and range-only interpretations
explicitly outside those complete-span assertions. For ambiguous instructions, also identify
the recorded address and exact decode or row digest; an address alone is not a
unique evidence key. See [the row formats](../EVIDENCE.md).

Change history and acceptance deltas belong in the reviewing PR and Git
history. Current decoding pitfalls stay with the affected finding. Maintainers
follow [the documentation update
rules](../MAINTAINING.md#documentation-updates).
