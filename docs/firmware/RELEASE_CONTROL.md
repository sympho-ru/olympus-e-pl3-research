# Release-control candidates

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

These routines provide concrete caller and input boundaries for investigating
still capture. The release-control name is a research hypothesis. A call or a
normal return does not yet identify an image-producing operation.

- [Release body and direct callers](#release-body)
- [Six-input frontend and control-object accessor](#six-input-frontend)
- [Candidate key-conversion owner](#key-conversion-owner)
- [Bounded selector-to-key lookups](#key-lookup)

<a id="release-body"></a>
## Release body and direct callers

The candidate body performs conditional lookups and calls further consumers.
Its direct callers provide concrete contexts for investigating a release
effect.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Release body | `0x6ebc92d7` | 0 | `0x005c92f7` | 528 |
| Body suffix | `local code view` | 0 | `0x005c950c` | 82 |
| Non-null helper | `0x6ebd9652` | 0 | `0x005d9672` | 153 |

The accepted block-0 spans at offsets `0x005c92f7` (528 bytes) and `0x005c950c`
(82 bytes) extend the local body at `0x6ebc92d7` through its return at
`0x6ebc953b`. These local addresses use `source + 0x6e5fffe0`; they are not a
global block mapping. The body contains conditional slot-`+12` lookups, a
direct call to `0x6ebd10b3` at `0x6ebc94e7`, and a call to `0x6ebd9652` at
`0x6ebc94ef`. At `0x6ebc94f6`, `cmp 0,d0` followed by `beq 0x6ebc9521`
selects the zero-status continuation; the other arm calls helpers and jumps to
the error return at `0x6ebc9444`. Neither outcome proves that an image was
produced.

The 153-byte helper span at offset `0x005d9672`, local `0x6ebd9652`, rejects
null incoming `a1`: `cmp 0,a2` / `bne 0x6ebd9662` follows `mov a1,a2`, and
the fallthrough returns `-268435434`. The remaining body contains indirect
slots `+16`, `+140`, `+144`, `+20`, and `+148` with conditional branches.
Concrete receiver identities and register preservation through those calls
remain unresolved. Supporting spans authenticate the initializer at
`0x6ec06fd8` (offset `0x00606ff8`, 17 bytes), the global-access window at
`0x6ebd1ddd` (offset `0x005d1dfd`, 95 bytes), and the seven-byte `a0 += 224` /
return at `0x6ebd1e73` (offset `0x005d1e93`).

Caller coverage includes the 145-byte body at `0x6eb8d802` (offset `0x0058d822`) and the ten-byte call/return wrapper at `0x6eb8cc42` (offset `0x0058cc62`).
Additional authenticated caller windows begin at `0x0058e1b9` (149 bytes),
`0x0058e785` (142 bytes), and `0x005c9a66` (381 bytes); each has only one
canonical instruction row, not a complete instruction listing. A 110-byte range
at `0x00860198` has source coverage without instruction rows.

**Unresolved:** a callable host entry, concrete receivers, and the connection
from the release-control candidate to capture or an image owner.

**Next evidence:** [Resolve the release-control body's indirect
consumers](../RESEARCH.md#r-release-contract).

<a id="six-input-frontend"></a>
## Six-input frontend and control-object accessor

The frontend passes six current destination words to a method of the object
returned by an accessor. Conversion validity and the selected method remain
unresolved.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Frontend | `0x6ebe36b0` | 0 | `0x005e36d0` | 696 |
| Control-object accessor | `0x6eb8c86f` | 0 | `0x0058c88f` | 88 |
| Initializer | `0x6eb8c8c7` | 0 | `0x0058c8e7` | 14 |

The 696-byte span at block-0 offset `0x005e36d0` covers the frontend at local
`0x6ebe36b0`, using `source + 0x6e5fffe0`. At `0x6ebe36b7`, `cmp 9,d0` /
`blt 0x6ebe36be` selects the lower-count arm; fallthrough jumps to `0x6ebe38bf`. That arm makes six calls to `0x6e8f6490`, with source pointers from incoming
`a0` fields `+12..+32` and stack destinations `sp+16..sp+36`. No
conversion-result branch occurs between these calls and the accessor call at
`0x6ebe392b`. Successful conversion, failure writes, and initializedness of
the destination words remain unproved.

After the accessor, the current words at `sp+28`, `+32`, and `+36` are copied
to outgoing stack slots `+4`, `+8`, and `+12`; words at `sp+16`, `+20`,
and `+24` are loaded into `d0`, `d1`, and `a1`. The frontend loads a table
through returned `a0`, selects slot `+304`, and executes `calls (a2)` at
`0x6ebe394a`. There is no intervening call between those loads and that
consumer. The indirect result is saved in `d2`, but the normal epilogue at
`0x6ebe3960` explicitly clears `d0`: frontend return zero is not evidence of
capture success.

The accessor at `0x6eb8c86f` (offset `0x0058c88f`, 88 bytes) tests global
`0x60357b54` and returns its current value. Its null path rechecks the global
after helper calls, passes `d0=8` to `0x6ee1bc13`, and conditionally calls the
14-byte initializer at `0x6eb8c8c7` (offset `0x0058c8e7`). That initializer
writes `0x6ee3f738` through `a0` and clears field `+4`. Allocation success,
helper preservation, and runtime receiver readiness remain unresolved; the
frontend does not check the returned pointer before dereferencing it.
Additional ranges authenticate three bytes at `0x00871e53` and 76 bytes at
`0x008747d4`, without adding instruction rows there. The installed word alone
does not establish its runtime table mapping or the slot-`+304` target. These
static relationships do not prove host ingress, still capture, image ownership,
or transfer.

**Next evidence:** [Establish frontend input and receiver
contracts](../RESEARCH.md#r-release-inputs).

<a id="key-conversion-owner"></a>
## Candidate key-conversion owner

Global access, initialization, and a table-word writer identify a candidate
key-conversion object. These spans have range-only support.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Global-access body | `0x6eb8ee29` | 0 | `0x0058ee49` | 93 |
| Initializer-shaped body | `0x6eb8f0b4` | 0 | `0x0058f0d4` | 68 |
| Key helper sequence | `0x6eb8f139` | 0 | `0x0058f159` | 35 |
| Table-word writer | `0x6eb92d6b` | 0 | `0x00592d8b` | 10 |
| Candidate data | `placement unresolved` | 0 | `0x0083f108` | 28 |

The first four spans use local code view `source + 0x6e5fffe0`.

The body at local `0x6eb8ee29` tests global `0x60357b60`, rechecks it after
helper calls, and on the remaining null arm passes `d0=28` to `0x6ee1bc13`. It
conditionally calls `0x6eb8f0b4`, stores the resulting `a0` in the global, and
later reloads the global before calling `0x6eb8f15c`. The latter entry lies
beyond the accepted 35-byte span; its behavior is not established by this span.

The initializer-shaped body at `0x6eb8f0b4` saves incoming `a0` in `a2`, calls
`0x6eb92d6b`, and forms subsequent helper arguments from `a2` at offsets `+4`, `+8`, `+12`, `+16`, `+20`, and `+24`. The ten-byte leaf at `0x6eb92d6b`
writes literal `0x6ee40528` through `a0`. The body at `0x6eb8f139` passes
`d0=0x02031902`, `d1=1`, `a0=6`, and `a1=5` to `0x6e872f9d`, then reloads
that key in `d0` before calling `0x6e872f3d`. Preservation through intervening
helpers, allocation success, and the concrete receiver/table relation remain
unresolved. The 28-byte range at `0x0083f108` supplies source coverage only;
the code display relation does not establish its runtime data mapping. These
spans do not prove conversion failure writes, initialized destination words,
runtime ownership, host ingress, capture, or image transfer.

**Next evidence:** [Connect the candidate key-conversion
owner](../RESEARCH.md#r-key-owner).

<a id="key-lookup"></a>
## Bounded selector-to-key lookups

Two leaves search eight-byte records for a selector and return a scalar key,
with zero on a miss. They contain no calls or destination-buffer writes. The
candidate source tables bound the possible keys only if their runtime placement
matches the literals read by these leaves; the caller and object connection
remain unresolved.

| Role | Recorded local address / data literal | Block | Offset | Length |
|---|---|---:|---|---:|
| Null-return leaf | `0x6eb941b5` | 0 | `0x00592d95` | 5 |
| First lookup | `0x6eb942fe` | 0 | `0x00592ede` | 41 |
| Second lookup | `0x6eb94327` | 0 | `0x00592f07` | 38 |
| First candidate key table | `0x6ee40408`, placement conditional | 0 | `0x0083efe8` | 160 |
| Second candidate key table | `0x6ee404a8`, placement conditional | 0 | `0x0083f088` | 128 |

The instruction rows use `source + 0x6e601420`, distinct from the
`source + 0x6e5fffe0` code view in the owner section. Adding the former delta
to the candidate data offsets matches the two literals, but this arithmetic
does not prove data placement or a call between the two code views.

The first leaf saves `d2`, clears it, and tests incoming selector `d0` at
`0x6eb94301`: `cmp d2,d0` / `blt 0x6eb94323` returns zero for a signed
negative selector. At `0x6eb94310`, `cmp d2,d1` / `bls 0x6eb94323` also
returns zero when the first record's key is zero. Otherwise the loop compares
record `+4` with `d0` at `0x6eb94318`. Inequality advances the record pointer
by eight at `0x6eb9431e`; equality loads the record's key into `d2` and exits
to `0x6eb94323`. The `cmp d2,d1` / `lhi` continuation repeats while the next
key is unsigned greater than zero. The exit copies the selected key or zero
to `d0` and restores the caller's `d2`.

The second leaf saves the selector in `d2` and clears result `d0`. Its
`cmp d0,d1` / `bls 0x6eb9434a` at `0x6eb94331` tests the first key; it has
no signed-negative input guard. The comparison at `0x6eb9433f` selects either
the matching key load into `d0` followed by exit to `0x6eb9434a`, or advancement
by eight at `0x6eb94345`. Its `cmp d0,d1` / `lhi` continuation stops on a
zero key, and the return restores `d2`. The seven conditional/unconditional
branch decodes in these two bodies are reproduced from the authenticated
ranges; they are not canonical instruction rows.

Interpreted as little-endian `(key, selector)` pairs, the first candidate table
has 19 nonzero records followed by `(0,0)`. Its selectors cover 1 through 18;
selector 13 appears twice. In source order its first match returns `0x02001707`,
so the later `0x0200170b` record is shadowed. The second candidate table has
15 nonzero records with selectors 1 through 15, followed by `(0,0)`. Conditional
on these being the runtime tables, selectors outside each domain return zero.
Neither leaf tests an explicit upper bound; the finite domains follow from the
candidate records and first-match search.

The separate five-byte leaf sets `a0=0` and returns without defining a key in
`d0`. None of these leaves establishes text-conversion success, initialized
frontend destinations, receiver readiness, or a capture effect.

**Next evidence:** [Connect the candidate key-conversion
owner](../RESEARCH.md#r-key-owner).
