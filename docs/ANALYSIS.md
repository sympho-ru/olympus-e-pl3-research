# Local firmware analysis

This workflow turns a contributor-supplied official image into private decoded
blocks and bounded disassembly windows. The decoded bytes remain local; public
contributions contain only the authenticated JSONL rows described in
[EVIDENCE.md](EVIDENCE.md).

## Extract verified decoded blocks

Place the official Body 1.6 image under `.private/`, verify it, and extract the
five decoded blocks:

```sh
epl3-research verify-source \
  --image .private/OLY_E_086_1600_0000_0000.BIN

epl3-research extract-blocks \
  --image .private/OLY_E_086_1600_0000_0000.BIN \
  --output .private/decoded
```

`extract-blocks` verifies the complete container and all block identities
before writing `block-0.bin` through `block-4.bin`. Inside this repository it
accepts only an output below `.private/`, and it refuses to overwrite an
existing block. The command prints filenames, sizes, and hashes, never the
decoded bytes.

`.private/` is ignored by Git. Never force-add its image, decoded blocks,
windows, logs, or tool output.

## Build an MN103-capable GNU objdump

The known-working reference for this project is
[GNU binutils 2.45](https://ftp.gnu.org/gnu/binutils/binutils-2.45.tar.xz),
available from the [official GNU archive](https://ftp.gnu.org/gnu/binutils/).
The archive also provides a
[detached signature](https://ftp.gnu.org/gnu/binutils/binutils-2.45.tar.xz.sig).
You need a C compiler, `make`, and system zlib development files.

Build only the required binary utilities inside the ignored private tree:

```sh
mkdir -p .private/toolchains
tar -xf /path/to/binutils-2.45.tar.xz -C .private/toolchains
mkdir .private/toolchains/binutils-2.45-build
cd .private/toolchains/binutils-2.45-build

../binutils-2.45/configure \
  --target=mn10300-elf \
  --disable-nls --disable-werror \
  --disable-gdb --disable-sim --disable-gas --disable-ld \
  --disable-gprof --disable-gold --disable-libctf \
  --with-system-zlib --disable-shared

make all-binutils
cd ../../..
```

Verify the resulting tool from the repository root:

```sh
MN103_OBJDUMP=.private/toolchains/binutils-2.45-build/binutils/objdump
"$MN103_OBJDUMP" --version
"$MN103_OBJDUMP" -i | grep mn103
```

The first command must identify GNU objdump 2.45. The target listing must
include `elf32-mn10300`, the `mn10300` architecture, and the `binary` input
format. If you already have a compatible build elsewhere, set
`MN103_OBJDUMP` to that executable instead.

## Reproduce the mapped PTP windows with GNU binutils

Create private windows at two authenticated block offsets:

```sh
mkdir -p .private/windows

dd if=.private/decoded/block-0.bin \
  of=.private/windows/ptp-record-init.bin \
  bs=1 skip=$((0x00d30925)) count=$((0x29))

dd if=.private/decoded/block-0.bin \
  of=.private/windows/byte-fill-helper.bin \
  bs=1 skip=$((0x0010cc15)) count=$((0x0f))
```

Disassemble each window at its explicit reviewed runtime address:

```sh
MN103_OBJDUMP=.private/toolchains/binutils-2.45-build/binutils/objdump

"$MN103_OBJDUMP" -z -b binary -m mn10300 -D --insn-width=16 \
  --adjust-vma=0x6f330905 .private/windows/ptp-record-init.bin

"$MN103_OBJDUMP" -z -b binary -m mn10300 -D --insn-width=16 \
  --adjust-vma=0x6e70cbf5 .private/windows/byte-fill-helper.bin
```

The window base is an authenticated runtime-address anchor. Do not apply a
single container-header load address to the entire decoded block: the current
evidence includes multiple block-0 runtime-address relationships.

Raw disassembly alone is not proof that every decoded boundary is executable
or reachable. Start from an accepted boundary, follow direct control flow, and
stop or record uncertainty at ambiguous data, indirect control, or decoder
disagreement.

## Cross-check with Reko

Reko is useful as an independent MN103 boundary and control-flow cross-check.
Use a revision containing the E-PL3-derived decoder corrections in
[Reko PR #1370](https://github.com/uxmal/reko/pull/1370), especially for
full-width `(d32,SP)` operands and PC-relative d32 `CALLS`.

Import the same private window as raw MN103 code and assign the same runtime
base used above (`0x6f330905` or `0x6e70cbf5`). Compare instruction addresses
and lengths before relying on higher-level control flow. This repository does
not bundle Reko or the earlier project-specific probe, so GNU reproduction is
the command-line baseline and Reko remains an optional independent check.

## Turn analysis into a contribution

For each accepted instruction boundary, record its runtime address, block,
block offset, length, textual decode, and slice SHA-256. Generate byte-free
range hashes with `epl3-research source-range`, then place sorted rows in
content-addressed files under `incoming/` as documented in
[CONTRIBUTING.md](../CONTRIBUTING.md).

Temporary conclusions and unsuccessful leads stay in `.private/` or the PR
discussion. New established subsystem meaning belongs in this small reviewed
map only after the maintainer accepts the underlying canonical evidence.
