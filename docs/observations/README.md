# Observations: reading, reporting, and review

Observations describe what happened under recorded conditions. They complement
the [static firmware reference](../FIRMWARE_MAP.md), which explains reviewed
source relationships. A successful download does not identify its firmware
implementation; a static call does not establish an observed camera effect.

## Read the reviewed observations

| Topic | What it records |
|---|---|
| [Deployment and handler experiments](DEPLOYMENT.md) | Specific modified images, post-boot markers, rejected requests, and one boot failure/recovery |
| [USB and media](USB_AND_MEDIA.md) | Session personalities, existing-photo retrieval, movie access, and capture/live-view limits |

Each result is limited to its recorded image, session, host, and action. Missing
historical metadata remains explicit. Source IDs such as D1 or U2 are local to
their page's source table; a digest identifies a retained file, not the truth
of an event or an independently reproducible public experiment.

## Name the result before the experiment

Use a descriptive title, for example “Version marker visible after reboot” or
“Selected JPEG downloaded in MTP mode.” An author's experiment identifier is
optional provenance, not a name that readers are expected to understand.
Introduce it with the purpose and scope, and qualify it by author/report when
needed. Different contributors can both have an experiment called `EXP-001`.

Public references use the report's repository path and descriptive section
anchor. There is no global experiment-number registry. The older `EXP-*`
labels in the deployment page are aliases from one historical series, explained
there alongside their readable names. They are not required identifiers for
new contributions.

## Submit an observation

Anyone, including the maintainer, uses the same reporting fields and acceptance
criteria. Positive results, bounded failures, and independent reproductions are
all useful. An incomplete identity may support a narrower result; do not invent
metadata to make a report appear complete.

1. Copy the [observation report template](TEMPLATE.md). Describe one bounded
   outcome, its conditions, what was measured versus reported by a person, and
   what remains unknown. Cite any related finding or earlier report.
2. Open a [GitHub issue](https://github.com/sympho-ru/olympus-e-pl3-research/issues/new)
   with the completed, sanitized report, or submit a documentation-only PR
   adding `docs/observations/reports/YYYY-MM-DD-short-description.md`. Choose a
   distinct descriptive suffix if that filename is already used. An issue
   requires no Git or firmware-analysis setup.
3. Identify the supporting records, their SHA-256 values where available, and
   whether they are public, available for maintainer inspection, or unavailable.
   Summarize relevant measurements in the report. Hashes alone do not establish
   the outcome. Do not attach firmware, packet dumps, personal media, device
   identifiers, secrets, private paths, or reconstruction-ready byte material.
   Arrange an appropriate review channel with the maintainer before sharing
   private supporting records; the public issue or PR is not that channel.
4. Respond to review questions and narrow claims when evidence is missing.
   The maintainer records acceptance, a qualified result, an existing matching
   finding, or the reason the evidence is insufficient. A submitted report is
   not part of the reviewed reference until its documentation is merged.

For a PR, follow the documentation checks in [MAINTAINING.md](../MAINTAINING.md#verify-documentation-changes).
An observation-only PR does not use `check-contribution` or `accept-contribution`:
those commands govern incoming static source rows. Submit new ranges or decoded
instructions separately through [CONTRIBUTING.md](../../CONTRIBUTING.md).

Reports describe completed observations; submission does not authorize someone
else to repeat a transfer, patch, or camera action. A proposed experiment must
be identified as a proposal, and a software rehearsal as a rehearsal.

## How acceptance works

The maintainer follows the [observation review procedure](../MAINTAINING.md#observation-review),
checks available primary support, records missing or withheld evidence, and
reviews the wording and publication boundary. The same review applies to the
maintainer's own reports. Identify who observed, authored, and reviewed the
result; self-review must not be described as independent reproduction.

Accepted reports receive a stable path/anchor and attribution. The relevant
topic page summarizes the resulting knowledge and links to the report; the
research question is narrowed or answered only within the supported scope.
Preserve independent reproductions as separate reports with their own conditions.
Correct a report in place with an explained review trail; retain its link and
make any superseded conclusion clear.
