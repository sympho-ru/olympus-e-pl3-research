# Firmware evidence format

The public evidence contains two sorted JSON Lines files. Each line is an
independently reviewable row; there are no topic wrappers, prose facts,
unresolved-question fields, contributor records, or extraction metadata.

## Authenticated ranges

`evidence/ranges.jsonl` contains exactly:

```json
{"block":0,"offset":8519680,"length":30,"sha256":"28df1ac852d06e22d1d9e551bf3742162a5703bd467140422e90b218f059fac4"}
```

- `block` identifies one decoded block from the registered Body 1.6 image.
- `offset` and `length` select the exact bytes inside that block.
- `sha256` authenticates the selected bytes without publishing them.

Rows are sorted by `(block, offset, length)` and coordinates are unique.

## Authenticated instructions

`evidence/instructions.jsonl` contains exactly:

```json
{"address":1865615393,"instruction":"call\t0x6f33093e,[a2,a3],24","block":0,"offset":13830209,"length":5,"sha256":"4054fa0b2f7cee3e6ae4ce0f563d2cac95318e45f8ff9e51f7a5cd4699f31fc6"}
```

The source coordinates and digest authenticate the original bytes. `address`
records the decoded runtime address as a decimal JSON integer; documentation
may show the same value in hexadecimal. It is distinct from the decoded-block
`offset` accepted by `source-range`. `instruction` records the reviewed textual
decode. The digest proves the source bytes, not the interpretation; reviewers
can reproduce the decode from their own verified image.

Rows are sorted by `(address, instruction, block, offset, length, sha256)` and
deduplicated. Multiple rows at one address remain valid when genuinely
different decodes were retained.

## Incoming contributions

Contributors never edit `evidence/`. They add one or more temporary files using
the same row schemas:

```text
incoming/ranges-<sha256>.jsonl
incoming/instructions-<sha256>.jsonl
```

`<sha256>` is the full lowercase SHA-256 of the exact file bytes, including the
final newline. Each file must be nonempty, sorted, and internally deduplicated.
A PR may contain any number of either file type; the PR itself groups them, so
there is no manifest or contributor metadata.

Exact canonical or repeated incoming rows are duplicates. A different range
hash for occupied coordinates, or different instruction text for an occupied
`(address, block, offset, length)` key, is a conflict requiring maintainer
review.

Incoming files are not part of the source of truth. The maintainer consumes
accepted files into the canonical set, and release checks reject any that
remain.

## Verification

Generate a range after verifying the complete official image:

```sh
epl3-research source-range \
  --image .private/OLY_E_086_1600_0000_0000.BIN \
  --block 0 --offset 0x1000 --length 32
```

Structural checks reject missing or additional fields, unexpected evidence
files, invalid bounds, invalid digest syntax, duplicates, and unsorted rows.
Firmware-backed checks recompute every digest from the verified image.

`check-contribution` applies the same validation only to incoming files, checks
their content-addressed names, scans them for prohibited payloads and private
paths, and proves the contributor did not modify canonical evidence.

Reviewed semantic relationships are documented separately in
[FIRMWARE_MAP.md](FIRMWARE_MAP.md); they never add fields to the canonical
evidence rows.
