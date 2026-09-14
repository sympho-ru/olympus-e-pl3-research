# Maintaining the evidence and documentation

This guide is for maintainers accepting reviewed contributions or updating the
public reference. Contributors follow [CONTRIBUTING.md](../CONTRIBUTING.md).
Canonical evidence acceptance and semantic interpretation remain separate
review responsibilities.

## Maintainer verification and acceptance

Treat every PR as untrusted. Pin its base and head commits, create an isolated
checkout, and inspect the complete diff before running anything from it. A
normal contribution changes only content-addressed `incoming/*.jsonl` files.
Run tests in the trusted target checkout, then use the trusted target-branch
installation to inspect the isolated PR checkout without importing or executing
code from the PR:

```sh
pytest
epl3-research check --root "$PR_ROOT"
epl3-research check-contribution \
  --root "$PR_ROOT" \
  --base "$BASE_SHA" \
  --source .private/OLY_E_086_1600_0000_0000.BIN
```

Review every new instruction decode against the authenticated source slice. If
a row cannot be reproduced, remove it on the contributor branch and give the
corrected file a fresh content-addressed name. Re-run all contributor checks on
the exact head that will be merged.

Merge the verified intake into the target branch with **Create a merge commit**.
Do not squash: keeping the contributor commits preserves their public authorship
and the reviewed head in repository history.

On the updated target branch, accept the files that passed review:

```sh
epl3-research accept-contribution \
  --source .private/OLY_E_086_1600_0000_0000.BIN \
  "$RANGE_FILE" \
  "$INSTRUCTION_FILE"
```

Pass only files being accepted; either file type may be omitted. This command
reverifies every selected file, performs a sorted set union into the canonical
files, ignores exact duplicates, fails before mutation on conflicts, and
deletes the consumed incoming files. It is intentionally a maintainer-only,
mutating command. Integrate immediately after the intake merge: release mode
rejects unconsumed incoming files, and a pending intake is not a suitable base
for another contribution.

Update the pinned corpus count, `AUTHORS.md` when authorship changes, the map
coverage table, and affected topic references and research questions following
[the documentation rules below](#documentation-updates). Keep research proposals and
semantic interpretations separate from mechanical evidence acceptance. Inspect
the complete integration diff, commit it, and run the final gates on that
committed `HEAD`:

```sh
pytest
epl3-research check
epl3-research check --source .private/OLY_E_086_1600_0000_0000.BIN
epl3-research check --release \
  --source .private/OLY_E_086_1600_0000_0000.BIN
```

Release mode fails if any unconsumed incoming file remains. Push the accepted
integration only after all four commands pass and the working tree is clean.

An exact duplicate needs no canonical change and is simply consumed. A claimed
correction intentionally conflicts with canonical evidence: review it
separately, edit the canonical row manually if the correction is established,
and remove the incoming file. Automatic acceptance never replaces or deletes
canonical evidence.

Do not commit firmware images, decoded blocks, byte dumps, private identifiers,
local paths, or analysis notes. Semantic interpretations do not yet have a
public schema and must not be inserted into evidence rows.

<a id="documentation-updates"></a>
## Update the current understanding in place

This is the shared editing contract for maintainers and AI coding agents.
Read the affected topic and its linked question before writing an acceptance
summary. A contribution's delta is review history; the reference describes the
resulting firmware understanding.

| Information | Home |
|---|---|
| Source coordinates, hashes, instruction text | The two canonical files under `evidence/` |
| Overview, block classification, coverage totals | [FIRMWARE_MAP.md](FIRMWARE_MAP.md) |
| Established relationships, source anchors, local limitations | The relevant page under `docs/firmware/` |
| Reviewed hardware/host observations and their evidence limits | The relevant page under `docs/observations/` |
| Missing evidence and the question it would answer | [RESEARCH.md](RESEARCH.md) |
| Address conventions, evidence terms, research labels | [Reading the references](firmware/READING.md) |
| Contribution history, changed-row counts, correction rationale | The reviewing PR and Git history |
| Temporary investigations, operational state, or rejected private leads | Private working material, outside the public reference |

For each accepted result:

1. Find the existing section by its stable anchor and source coordinates.
   Rewrite its current explanation instead of appending an acceptance paragraph.
   Add a section only for a distinct relationship that has no existing home.
2. Preserve source coordinates, address-view qualifications, branch outcomes,
   argument definitions, register effects, and object identities needed for the
   conclusion. Keep range-only support distinct from canonical instructions.
3. State the result in plain language before presenting the technical detail.
   Use an anchor table when several exact ranges need comparison, and a field
   or slot table when it makes the relationships easier to read.
4. Update the linked research question when the missing evidence changes.
   Consolidate duplicate questions. Close an answered question with a link to
   the finding while retaining its ID; partial evidence only narrows it.
5. Update the overview only when its summary or coverage changes. Add a glossary
   explanation for a new research label; use coordinates when its meaning is
   unknown. Keep old links working when moving or renaming a section.

Avoid relative history such as “now canonical,” “newly accepted,” or “this intake”
in the reference. Keep enduring decode pitfalls beside the affected finding;
keep replacement counts and correction chronology in the PR. The common static
evidence limit is explained once in the reading guide, but specific missing
joins and preservation/mapping uncertainties must stay beside their claims.

An entry should answer these questions in this order:

```text
Plain-language result and role of this area
Source anchors: block, offset, length; local addresses where supported
Established relationships: operations, conditions, and object identities
Unresolved boundary or interpretation pitfall specific to this result
Link to the stable research question
```

The wording and use of tables can vary with the finding. Do not add fields to
canonical evidence, duplicate the reference in a second claims database, or
copy private campaign instructions into public docs. A successful mechanical
gate cannot replace semantic review.

## Retain knowledge that does not add source rows

A result can add a relationship, an empirical observation, a bounded negative,
or a correction without adding a range or instruction. During review, identify
its lasting knowledge and destination, or explain why existing documentation
already covers it. Record that disposition in the reviewing PR. Do not require
a duplicate or artificial incoming row to justify a documentation update.

Historical and empirical reports receive maintainer review separately from
normal incoming-only contributions. Before admitting an observation:

1. Inspect its primary outcome and available supporting artifacts. Bind the
   retained source files by SHA-256 and keep the private path/field mapping.
   Historical chat or summary prose can locate evidence; it is not automatic
   authority. Identify any user-attested step explicitly.
2. Record date, model, exact parent/candidate image identities where known,
   relevant host/tool versions, camera personality/session state, action,
   response, and limitations. Leave missing metadata explicit. Separate a
   host-tool error, captured camera rejection, simulation, and physical outcome.
3. Publish an authored, sanitized account with stable observation/source IDs
   and enough selected measurements to assess the conclusion. State which
   evidence is private and cannot be independently replayed from the public
   repository. A source hash is an identity check, not event authentication.
4. Review publication rights and remove firmware/packet dumps, personal media,
   device identifiers, secrets, and private paths. Preserve original records
   privately. An observation page is not an executable experiment or approval
   record; retired designs remain retired.
5. Link the observation from the affected topic/map and narrow the associated
   research question. Preserve the distinction between demonstrated capability
   and an unidentified static implementation or missing end-to-end connection.

Do not add observation fields or files under `evidence/`, change the registered
official image to accommodate candidates, or weaken the incoming/contextual
gates. New static support still follows ordinary evidence admission. Track
historical reconciliation privately against declared source snapshots; report
remaining gaps rather than asserting that an unchecked archive is complete.

## Verify documentation changes

Run `pytest` and `epl3-research check` after editing. Documentation tests check
relative Markdown links and fragment targets, exact canonical range anchors in
source tables, and the map's per-block counts. They require no firmware.
They do not prove prose semantics or runtime placement.

For a reorganization, compare the moved findings with the previous revision:
preserve each substantive relationship and local limitation, account for any
removed history, and inspect the rendered navigation and tables. A coordinate
inventory helps catch omissions but does not prove that the reasoning survived.

Run the source/release gates above on the committed revision before publication.
The release audit covers the public tree and reachable Git history; it does not
audit GitHub issue or PR text. Review externally posted prose under the same
publication boundary. A documentation-only refactor must leave the canonical
evidence byte-for-byte unchanged unless a separate correction is explicitly
part of the task.
