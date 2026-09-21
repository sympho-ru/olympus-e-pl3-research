# Working in this repository

This is the public, byte-free Olympus E-PL3 Body 1.6 evidence repository.
Use [README.md](README.md) for setup and publication boundaries.

## Find the right source

- [FIRMWARE_MAP.md](docs/FIRMWARE_MAP.md) is the overview and topic index.
- [Reading conventions](docs/firmware/READING.md) define source coordinates,
  local address views, evidence limits, and research labels.
- `docs/firmware/` holds the reviewed relationships. Open the affected topic
  and its source anchors before changing a conclusion.
- `docs/observations/` holds reviewed historical hardware and host results.
  Check these before describing a capability as unproved. Preserve exact
  image/session scope and distinguish measurements, attestations, and rehearsals.
  Its [reporting guide](docs/observations/README.md) separates submissions from
  accepted observations; explain local experiment labels in plain language.
- [RESEARCH.md](docs/RESEARCH.md) holds open questions with stable IDs. It is
  not a live campaign queue and does not repeat the detailed findings.
- [CONTRIBUTING.md](CONTRIBUTING.md) governs incoming-only evidence submissions.
- [MAINTAINING.md](docs/MAINTAINING.md) governs maintainer acceptance and
  [documentation updates](docs/MAINTAINING.md#documentation-updates).
- [DECODING.md](docs/DECODING.md) governs contextual verification and correction
  review. A canonical row or successful decode does not establish execution.

## Editing and verification

Update an existing finding in place and narrow or close its linked question.
Give each detailed explanation one home; use links from summaries and questions.
Preserve exact source anchors, conditional address views, branch outcomes,
register preservation boundaries, and distinct object identities. Put acceptance
deltas in the PR description. Use plain language before technical detail.

Do not infer capture, image ownership, or host transfer from a label, scalar
return, table, or queued copy. Use the canonical evidence and current reviewed
references, not private findings or a previous task's summary, for public claims.
Keep temporary scripts, firmware, decoded bytes, and working notes in `.private/`.

Historical observation backfills follow the separate review in
`docs/MAINTAINING.md`; private summaries alone do not establish a public finding.
A result with no new source rows can still require a reviewed documentation
update. Record its knowledge disposition in the PR, without changing the
incoming-only evidence workflow or turning open questions into campaign jobs.

Run `pytest` and `epl3-research check` for changes here. Follow the source and
committed-release gates in the maintainer guide for publication. Documentation
tests check navigation, typed source references, and coverage counts; review
the meaning of rewritten claims separately. Follow the user's authorized scope
for commits, PRs, acceptance, and merges.
