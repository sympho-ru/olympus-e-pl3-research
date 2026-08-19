# Olympus E-PL3 firmware research

The goal of this project is to give the Olympus E-PL3 a second life with custom
firmware. Reaching that goal requires a verifiable understanding of the
original Body 1.6 firmware, so this repository publishes source ranges and
decoded instructions that contributors can extend without redistributing
Olympus firmware.

The canonical public data is:
- `evidence/ranges.jsonl`: verified firmware coordinates and slice hashes
- `evidence/instructions.jsonl`: decoded instructions tied to verified slices

These files are updated by the maintainer. Refer to
[CONTRIBUTING.md](CONTRIBUTING.md) for submission and acceptance steps.

## Where to start

- To see what is already known, read the
  [firmware map](docs/FIRMWARE_MAP.md).
- To reproduce the work locally, first
  [obtain and verify the official image](docs/OBTAINING_FIRMWARE.md), then
  follow the [analysis workflow](docs/ANALYSIS.md).
- To extend the research, choose an open question in
  [RESEARCH.md](docs/RESEARCH.md) and follow [CONTRIBUTING.md](CONTRIBUTING.md).
- For the exact canonical and incoming row formats, see
  [EVIDENCE.md](docs/EVIDENCE.md).

## Quick start

Python 3.11 or newer is required.

```sh
python3 -m venv .private/venv
.private/venv/bin/pip install -e '.[test]'
epl3-research check
epl3-research verify-source --image .private/OLY_E_086_1600_0000_0000.BIN
epl3-research check --source .private/OLY_E_086_1600_0000_0000.BIN
```

`check` validates file shape, sorting, bounds, digest syntax, licensing, and
public-tree hygiene without requiring firmware. `check --source PATH` also
verifies the official image and recomputes every cited slice SHA-256.

Ongoing MN103 analysis cross-checks instruction boundaries with GNU binutils
and Reko. [ANALYSIS.md](docs/ANALYSIS.md) shows how to obtain the known-working
MN103 objdump and reproduce the first mapped corridor without placing decoded
firmware in the public tree.

To verify a contribution without rechecking every canonical row:

```sh
epl3-research check-contribution \
  --base origin/main \
  --source .private/OLY_E_086_1600_0000_0000.BIN
```

The command proves that canonical evidence was not modified, verifies the
content-addressed incoming files, authenticates only their firmware slices,
and reports instruction decodes requiring review. See
[CONTRIBUTING.md](CONTRIBUTING.md) for submission and acceptance steps.

Release mode additionally audits configured private terms and all blobs
reachable from the checked-out `HEAD`. It fails while any incoming submission
remains unconsumed:

```sh
epl3-research check --release --source .private/OLY_E_086_1600_0000_0000.BIN
```

## Publication boundary

This distribution contains no Olympus firmware image, decoded block,
binary/archive payload, declared encoded byte dump, or reconstruction-ready
firmware region. The project publishes coordinates, lengths, hashes, and
instruction text. Contributors provide their own bit-identical official image;
the project provides no firmware mirror or downloader.

Short functional identifiers may appear when needed to describe the firmware.
Firmware-originated prose or other potentially expressive text requires
explicit maintainer review and is omitted unless essential.

Olympus and PEN are trademarks of their respective owners. This independent
project is not endorsed by OM Digital Solutions or Olympus.

## Licensing and maintenance

Code is licensed under Apache-2.0. Authored documentation and evidence metadata
are licensed under CC BY 4.0. See [AUTHORS.md](AUTHORS.md) for maintainer credit;
contributor authorship remains recorded in Git history.
