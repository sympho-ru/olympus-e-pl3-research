This repository contains source ranges and decoded instructions of the original
Olympus E-PL3 Body 1.6 firmware.

The canonical public data is:
- `evidence/ranges.jsonl`: verified firmware coordinates and slice hashes
- `evidence/instructions.jsonl`: decoded instructions tied to verified slices

These files are updated by the maintainer. Refer to
[CONTRIBUTING.md](CONTRIBUTING.md) for submission and acceptance steps.

See [EVIDENCE.md](EVIDENCE.md) for the exact row formats and
[OBTAINING_FIRMWARE.md](OBTAINING_FIRMWARE.md) for the official source identity.

There is no public semantic annotation layer yet. It may be added separately
after firmware-only annotations have been curated.

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

## Licensing and authorship

Code is licensed under Apache-2.0. Authored documentation and evidence metadata
are licensed under CC BY 4.0. See [AUTHORS.md](AUTHORS.md) for authorship.