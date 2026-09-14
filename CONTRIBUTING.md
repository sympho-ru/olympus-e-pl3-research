# Contributing firmware evidence

The maintainer owns the two canonical files under `evidence/`. Contributors
submit temporary, content-addressed JSONL files under `incoming/` using the
same range or instruction row schema.

See [RESEARCH.md](docs/RESEARCH.md) for open questions and suggested starting
regions. Contributions may overlap; acceptance depends on the evidence rather
than prior assignment.

[ANALYSIS.md](docs/ANALYSIS.md) shows how to build the known-working MN103
objdump, extract verified blocks privately, and reproduce the first mapped
windows. [FIRMWARE_MAP.md](docs/FIRMWARE_MAP.md) states the currently
established relationships and their unresolved bounds.

## Preparing a contribution

1. Start a branch from the current target branch and keep it up to date so that
   the chosen `--base` ref is an ancestor of your `HEAD`.
2. Obtain and verify the exact Body 1.6 image.
3. Keep tools, logs, notes, temporary bytes, and extraction details outside the
   public tree, normally under `.private/`.
4. Write one or more nonempty, sorted, deduplicated JSONL files using the row
   formats in [EVIDENCE.md](docs/EVIDENCE.md).
5. Hash each exact file and use its full lowercase digest in the filename:

```sh
mkdir -p incoming
digest=$(shasum -a 256 draft-ranges.jsonl | awk '{print $1}')
mv draft-ranges.jsonl "incoming/ranges-${digest}.jsonl"
```

Use `instructions-<sha256>.jsonl` for instruction rows. Changing a file changes
its required filename. Do not edit `evidence/ranges.jsonl` or
`evidence/instructions.jsonl`.

Run:

```sh
pytest
epl3-research check
epl3-research check-contribution \
  --base origin/main \
  --source .private/OLY_E_086_1600_0000_0000.BIN
```

The contribution check requires an exact official image, proves that canonical
evidence matches the base ref byte-for-byte, verifies only submitted slices,
reports duplicates and conflicts, and scans incoming text for prohibited
firmware payloads, secrets, and private paths. It does not prove instruction
interpretation; new instruction decodes remain a maintainer review item.

Open a PR that adds only the `incoming/` files. No manifest, identity record,
method description, or public analysis log is required. A short PR description
identifying the covered address region and decoder is useful review context but
is not canonical evidence. Contributor commits and the merge commit preserve
public attribution in repository history; [`AUTHORS.md`](AUTHORS.md) identifies
the maintainer. State a preferred public name or handle in the PR if it differs
from the public commit and GitHub identity.

When using Reko for MN103 instruction rows, use a revision containing the
decoder fixes from [Reko PR #1370](https://github.com/uxmal/reko/pull/1370) for
full-width `(d32,SP)` operands and PC-relative d32 `CALLS`, or independently
cross-check those instruction boundaries.

<a id="maintainer-verification-and-acceptance"></a>
## After submission

The maintainer verifies the exact contribution, merges the reviewed intake,
and consumes the selected incoming files into canonical evidence. See
[maintainer verification and acceptance](docs/MAINTAINING.md#maintainer-verification-and-acceptance)
for that procedure. Contributors do not update canonical files or the reviewed
topic references as part of an incoming-evidence PR.

For a historical finding or hardware observation that cannot be represented by
source rows, provide the maintainer a sanitized description of the conditions,
result, evidence availability, and limitations. It receives a separate
[documentation review](docs/MAINTAINING.md#retain-knowledge-that-does-not-add-source-rows).
Do not put raw captures, personal media, private identifiers, or experimental
metadata into an incoming-evidence PR. Maintainer review can retain useful
knowledge even when no new source row is needed.

## Contextual instruction gate

Instruction intake requires GNU MN103 objdump 2.45 through `MN103_OBJDUMP` or
`--objdump`. Both contribution verification and maintainer acceptance enforce
complete lengths and text against contextual source windows. Overlapping rows
require exact pair adjudication; a decode defect cannot be waived. See
[DECODING.md](docs/DECODING.md) for commands and review format.

For decisive semantic conclusions, explicitly reproduce branch outcomes and
argument/register definitions through intervening calls to the consumer. A
valid decode or known call target does not establish register preservation.
State unresolved anchors or joins and withhold unsupported conclusions.

## Contribution licensing

By submitting a contribution for inclusion in this project, you agree to
license code under [Apache-2.0](LICENSE) and authored documentation and evidence
metadata under [CC BY 4.0](LICENSE-DOCUMENTATION). You also confirm that you
have the right to submit the contribution under those terms.
