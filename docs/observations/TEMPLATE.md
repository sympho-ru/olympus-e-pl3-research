# Observation: descriptive result title

Copy this template into an issue or a documentation-only PR as described in
[Submitting an observation](https://github.com/sympho-ru/olympus-e-pl3-research/blob/main/docs/observations/README.md#submit-an-observation). Replace the prompts
with the actual record; use “unknown” or “not recorded” where appropriate.
This template contains no experimental result.

## Result and scope

State the observed result in plain language and the exact conclusion it supports.
Distinguish a completed observation from a proposal or rehearsal. State what the
result does not establish and link any related report, finding, or question.

## Conditions

| Field | Recorded value |
|---|---|
| Date/time and timezone | Not recorded |
| Observer and report author | Public name or handle, with consent |
| Camera model | Unknown; omit serial numbers and other device identifiers |
| Firmware identity | Exact image hash/parent and candidate identities if known; distinguish delivered artifact from readback |
| Displayed versions | Identify camera-menu version versus DeviceInfo marker; neither substitutes for an image hash |
| Host and tools | Relevant OS/tool versions, or not recorded |
| Camera/session state | USB personality, session/interface ownership, and relevant initial state |
| Author's local experiment label | Optional; explain its purpose; it is not a repository-wide identifier |

## Action and outcome

Describe what was actually done, the expected result if relevant, the observed
response, and any controls or repeated attempts. Give selected byte-free
measurements sufficient to assess the conclusion: for example response code,
transaction match, object count, saved size/hash, or visible outcome.

Separate captured device responses, host-tool errors, user attestations, and
simulation results. Identify which records support each statement. Do not infer
capture from button response or identify a firmware handler from an operation
name. Record uncertain or missing conditions beside the affected conclusion.

## Supporting records

| Local source ID | Record description and evidence class | SHA-256, if available | Availability and limitation |
|---|---|---|---|
| S1 | Describe the record and whether it is a measurement, attestation, or rehearsal | Not supplied | Public sanitized record, privately reviewable, or unavailable; explain missing metadata |

Use IDs only within this report and explain empty logs or withheld records.
Include links only to material suitable for public publication. A hash binds
contents; it does not authenticate an event. Do not include private paths or
prohibited payloads. Document whether primary records could be inspected and
what a public reader can independently verify.

## Limitations and follow-up question

State applicability, alternative explanations, and the smallest unresolved
question. Do not turn a failed route into proof that every route fails.
Any proposed follow-up is separate from the completed observation.

## Attribution and review

Confirm that you can publish the authored report under the repository's
CC BY 4.0 documentation license and describe any restrictions on supporting
records. Do not publish another person's records without permission.

The maintainer completes the disposition in the reviewing issue/PR and records
its link here when the report is accepted: reviewer, evidence inspected,
supported conclusion and qualifications, destination finding, and research-question
change or reason none is needed. Identify self-review explicitly. Leave this
section pending during submission; do not pre-label a proposal as accepted.
