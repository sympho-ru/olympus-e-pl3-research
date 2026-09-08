# Repaired instruction regressions

Byte-free original and repaired rows from the reviewed PR 66, 70, and 72
corrections. The originals include wrapped-width truncations, operand-fragment
records, and the separately adjudicated overlapping jump. The fixed set
contains full-width decodes; inclusion here does not establish alternate-entry
reachability. These files are test data, never canonical evidence.

Run the real-source regression by setting `OLYMPUS_IMAGE` and `MN103_OBJDUMP`.
The default tests require no firmware or external decoder. No bytes or private
paths are embedded in these fixtures.
