# Working in this repository

This is the public, byte-free Olympus E-PL3 Body 1.6 evidence repository.
Use [README.md](README.md) for setup and publication boundaries.

## Find the right source

- [FIRMWARE_MAP.md](docs/FIRMWARE_MAP.md) is the overview and topic index.
- [Reading conventions](docs/firmware/READING.md) define source coordinates,
  local address views, evidence limits, and research labels.
- `docs/firmware/` holds the reviewed relationships. Open the affected topic
  and its source anchors before changing a conclusion.
- [RESEARCH.md](docs/RESEARCH.md) holds open questions with stable IDs. It is
  not a live campaign queue and does not repeat the detailed findings.
- [CONTRIBUTING.md](CONTRIBUTING.md) governs incoming-only evidence submissions.
- [MAINTAINING.md](docs/MAINTAINING.md) governs maintainer acceptance and
  [documentation updates](docs/MAINTAINING.md#documentation-updates).
- [DECODING.md](docs/DECODING.md) governs contextual verification and correction
  review. A canonical row or successful decode does not establish execution.

## Editing and verification

Update an existing finding in place and narrow or close its linked question.
Preserve exact source anchors, conditional address views, branch outcomes,
register preservation boundaries, and distinct object identities. Put acceptance
deltas in the PR description. Use plain language before technical detail.

Do not infer capture, image ownership, or host transfer from a label, scalar
return, table, or queued copy. Use the canonical evidence and current reviewed
references, not private findings or a previous task's summary, for public claims.
Keep temporary scripts, firmware, decoded bytes, and working notes in `.private/`.

Run `pytest` and `epl3-research check` for changes here. Follow the source and
committed-release gates in the maintainer guide for publication. Documentation
tests check navigation, canonical range references, and coverage counts; review
the meaning of rewritten claims separately. Follow the user's authorized scope
for commits, PRs, acceptance, and merges.
