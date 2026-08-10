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
is not canonical evidence.

When using Reko for MN103 instruction rows, use a revision containing the
decoder fixes from [Reko PR #1370](https://github.com/uxmal/reko/pull/1370) for
full-width `(d32,SP)` operands and PC-relative d32 `CALLS`, or independently
cross-check those instruction boundaries.

## Maintainer verification and acceptance

On a current local checkout of the PR:

```sh
pytest
epl3-research check
epl3-research check-contribution \
  --base origin/main \
  --source .private/OLY_E_086_1600_0000_0000.BIN
```

Review every new instruction decode against the authenticated source slice.
After accepting the reported additions, run:

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
mutating command.

Then inspect the canonical diff and run:

```sh
pytest
epl3-research check
epl3-research check --source .private/OLY_E_086_1600_0000_0000.BIN
epl3-research check --release \
  --source .private/OLY_E_086_1600_0000_0000.BIN
```

Release mode fails if any unconsumed incoming file remains. Add the acceptance
result to the PR branch and squash-merge it, or reproduce the same acceptance
on a maintainer integration branch.

An exact duplicate needs no canonical change and is simply consumed. A claimed
correction intentionally conflicts with canonical evidence: review it
separately, edit the canonical row manually if the correction is established,
and remove the incoming file. Automatic acceptance never replaces or deletes
canonical evidence.

Do not commit firmware images, decoded blocks, byte dumps, private identifiers,
local paths, or analysis notes. Semantic interpretations do not yet have a
public schema and must not be inserted into evidence rows.

## Contribution licensing

By submitting a contribution for inclusion in this project, you agree to
license code under [Apache-2.0](LICENSE) and authored documentation and evidence
metadata under [CC BY 4.0](LICENSE-DOCUMENTATION). You also confirm that you
have the right to submit the contribution under those terms.
