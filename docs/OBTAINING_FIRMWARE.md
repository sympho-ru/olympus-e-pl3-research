# Obtaining and verifying the official firmware

The project does not distribute or mirror Olympus firmware and does not include
an automatic downloader. Obtain the official E-PL3 Body 1.6 image through a
lawful source available to you. Upstream availability is not guaranteed.

`verify-source` requires this exact container identity:

- Filename: `OLY_E_086_1600_0000_0000.BIN`
- Size: `46,596,160` bytes
- SHA-256: `89b70dd65c6739de1cd762777205953ee15864df73369b84815df7ed8a0eb4b1`

The verified container must decode to exactly five blocks:

| Block | Size | SHA-256 |
| ---: | ---: | --- |
| 0 | 14,155,712 | `c291722827a5120fc06ca288b439cae82ebf597ac2cd83eba30a7f0fe6a72687` |
| 1 | 23,068,608 | `af5a35e02304183c9e716af99b9fb619abb13f5a71e41146986bf9d833e2e20f` |
| 2 | 2,490,304 | `ae9d7a1cc5f0d3bfeedb4dfecedc70be8a423e9bea7070cee16363fb30eaacfb` |
| 3 | 6,815,680 | `218b6003e490efc432851e831086cf8f1237f2fde3fade4be93dd89425459941` |
| 4 | 65,536 | `e131370def9d69fe4484592f0cf4bc84c865162007c0cae11405a4911c8b07a2` |

Place the image under `.private/` and run:

```sh
epl3-research verify-source --image .private/OLY_E_086_1600_0000_0000.BIN
```

Failures print both expected and actual filename, size, or SHA-256. Container
and decoded-block failures identify the affected block and expected/actual
values. A mismatch means this image cannot be used for source-range or release
verification; renaming a different image is not sufficient.

After verification, a contributor can create a byte-free citation without
printing or writing the selected bytes:

```sh
epl3-research source-range \
  --image .private/OLY_E_086_1600_0000_0000.BIN \
  --block 0 --offset 0x1000 --length 32
```

The command prints block, offset, length, and the SHA-256 of the exact selected
slice. It never prints or writes the selected bytes. Contributors place output
in a sorted `incoming/ranges-<sha256>.jsonl` file as described in
[CONTRIBUTING.md](../CONTRIBUTING.md); they never edit canonical `evidence/`
files directly.
Firmware-backed checks recompute every digest so an incorrect coordinate,
length, or hash fails closed.

For local reverse engineering, `extract-blocks` writes all verified decoded
blocks only to a private output directory and refuses to overwrite them. See
[ANALYSIS.md](ANALYSIS.md) for the safe extraction and MN103 disassembly
workflow. Decoded blocks and analysis windows must never be committed.
