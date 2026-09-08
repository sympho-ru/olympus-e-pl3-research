# Contextual instruction verification

`check-contribution` and `accept-contribution` now enforce a shared MN103
instruction check before acceptance writes any canonical rows. Range-only
contributions do not require a decoder. Existing structural, source-hash and
release checks retain their documented meaning; none certifies instruction
semantics or the correctness of all historical evidence.

Use GNU MN103 objdump 2.45, built as described in [ANALYSIS.md](ANALYSIS.md):

```sh
export MN103_OBJDUMP=.private/toolchains/binutils-2.45-build/binutils/objdump
epl3-research check-contribution --base origin/main --source .private/official.BIN
epl3-research accept-contribution --source .private/official.BIN incoming/instructions-HASH.jsonl
```

`--objdump` overrides the environment variable. A missing or incompatible tool
fails instruction intake; it never falls back to hash-only acceptance. The
current verifier supports block-0 MN103 instructions. Other architectures need
an explicit verifier before their instruction rows can be accepted.

## What is checked

The verifier authenticates submitted slices, joins touching source intervals,
and decodes with lookahead beyond the claimed lengths. GNU binutils 2.45's
`opcodes/m10300-dis.c` assigns at most seven bytes to MN103 instruction forms;
therefore six additional bytes beyond the cited interval suffice to complete
an instruction starting at its last byte. Source block boundaries are never
crossed. Wrapped byte lines are joined; orphan continuations are rejected.
Zero bytes are disassembled with `-z`.

Every row must match the complete decoded length and instruction text. Text
comparison normalizes whitespace only. Unknown encodings and assembler data
pseudo-operations are not accepted as instructions. Reports contain hashes,
coordinates and instruction text, never raw byte columns or tool diagnostics.

The gate also decodes nearby canonical starts and compares overlapping source
intervals using both observed and recorded lengths. A corrected long row cannot
silently coexist with its truncated predecessor. Intersections are checked even
when the runtime-address mapping differs.

All start anchors remain hypotheses in this mechanical report. Contiguous
linear decoding does not prove execution through embedded data or establish
branch reachability. An interior start is decoded independently and flagged for
review. Successful decoding must not be described as an established caller path.

## Screen existing evidence or a proposed instruction file

```sh
epl3-research screen-instructions --source .private/official.BIN \
  --output .private/instruction-screen.json

epl3-research screen-instructions --source .private/official.BIN \
  --output .private/proposal-screen.json incoming/instructions-HASH.jsonl
```

The first form screens the canonical corpus. The second checks selected rows
and intersecting canonical evidence. Exit status is 0 for no findings, 1 for
decode defects or overlaps requiring review, and 2 for an operational/schema
error. Evidence is never changed. The report records the source, canonical
instruction file, decoder binary and verifier digests.

Do not equate every overlap or text mismatch with corrupt evidence. Review the
reported rows, reproduce a window from a justified anchor, and distinguish
actual truncation, formatting disagreement and alternate decode hypotheses.
For a confirmed defect, make a reviewed canonical correction and explain its
reason in the correction PR. Recheck the affected conclusions in the map.

## Retaining legitimate alternate decodes

Acceptance requires an explicit decision for every overlapping pair, including
pairs within one submission. Copy the exact pair from the screen report into
a local review file and add its reason:

```json
{"overlaps":[{"rows":["ROW_ID_FROM_REPORT_A","ROW_ID_FROM_REPORT_B"],"reason":"Explain why both exact decodes are retained, their anchor evidence, and any unresolved entry status."}]}
```

Pass that file with `--overlap-review .private/overlap-review.json`. IDs are
SHA-256 of the complete normalized JSON object (sorted keys and compact JSON),
including source coordinates and slice hash. They are report references, not
new canonical row fields. A changed row requires a new decision. Missing,
duplicate or unrelated pair decisions fail. A review cannot waive a decode or
source mismatch: correct those rows first. Preserve the pair and rationale in
the maintainer's PR review record.

## Review the reasoning that matters

Before admitting a decisive semantic conclusion, record:

- The compare/test address, operands, taken condition and fallthrough outcome.
- The defining instructions for relevant arguments/registers, intervening calls
  and writes, and the consuming instruction. Establish preservation explicitly.
- The source/address anchor and the exact unresolved boundary.

Apply this to range-only and zero-row conclusions too. If evidence is missing,
withhold that conclusion. The private curation prompt uses these same criteria;
its final instruction reproduction calls this shared verifier and withholds
all overlaps for maintainer adjudication. No database or claims ledger is needed.

## Regression checks

The standard test suite uses synthetic instructions and needs no firmware.
Setting `OLYMPUS_IMAGE` and `MN103_OBJDUMP` also runs the byte-free original and
repaired PR 66/70/72 regression fixtures against the verified official source.
It checks that defective records are rejected or flagged as intersecting starts,
while full-width replacements reproduce. Alternate-entry reachability remains
a separate review question.
