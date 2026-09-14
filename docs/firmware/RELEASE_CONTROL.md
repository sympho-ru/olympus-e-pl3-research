# Release-control candidates

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

These routines provide concrete caller and input boundaries for investigating
still capture. The release-control name is a research hypothesis. A call or a
normal return does not yet identify an image-producing operation.

- [Release body and direct callers](#release-body)
- [Guarded action and carrier calls](#guarded-action)
- [Caller record and scalar consumer](#caller-record)
- [Constructed service and receiver selection](#constructed-service)
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

<a id="guarded-action"></a>
## Guarded action and carrier calls

The action at source `0x005c9e20` checks two helper results, prepares a carrier,
and calls methods through unresolved receivers. Its direct callers establish
local entry edges, but the method effects do not identify capture initiation.
These relationships have authenticated range support; this action and its
carrier helpers do not have canonical instruction listings.

| Role | Local address | Block | Offset | Length |
|---|---|---:|---|---:|
| Preceding return and action prologue | `0x6ebc9df8` | 0 | `0x005c9e18` | 8 |
| Action body through return | `0x6ebc9e00` | 0 | `0x005c9e20` | 174 |
| First guard helper | `0x6ebd1a61` | 0 | `0x005d1a81` | 14 |
| Second guard helper | `0x6ebd1aa6` | 0 | `0x005d1ac6` | 15 |
| Carrier construction | `0x6ebd2634` | 0 | `0x005d2654` | 70 |
| Nested field writer | `0x6eb9a781` | 0 | `0x0059a7a1` | 19 |
| Dynamic-call body | `0x6eb9a11c` | 0 | `0x0059a13c` | 77 |
| Conditional state helper | `0x6ebd8569` | 0 | `0x005d8589` | 30 |
| Direct wrapper | `0x6ebe6b0a` | 0 | `0x005e6b2a` | 28 |
| Wrapper's accessor chain | `0x6ebd1b56` | 0 | `0x005d1b76` | 13 |
| Conditional caller fragment | `0x6ebd3595` | 0 | `0x005d35b5` | 85 |

This section uses local code view `source + 0x6e5fffe0`. The action's prologue
starts at source `0x005c9e1b`; the 174-byte body ends at `0x005c9ece`, with its
final return starting at `0x005c9ecb`. The wrapper calls the accessor chain,
then the action at source `0x005e6b34`, and later clears its own return `d0`.
The other fragment loads field `+176` from the current stack-supplied object
before its action call at `0x005d35de`; the earlier slot-`+8` result must differ
from current `d2` at `0x005d35d5` to reach this arm. The fragment does not define
that comparison's original `d2` value.

The action saves incoming `a0` in `a2`. At source `0x005c9e26` and
`0x005c9e39`, each `cmp 0,d0` / `beq` continues only on zero. The nonzero
arms return `-268435455` and `-268435422`, respectively. Each guard helper
loads receiver field `+4` and calls local `0x6ec0672d`, with `d0=0` or `5`;
the meaning of those checks remains unresolved.

On the continuation, the action prepares `sp+12` in `a3`, loads through the
current `a2+52`, and calls two helpers. Immediately before construction at
source `0x005c9e76`, it supplies current `a3` in `a0`, current `d2` in `a1`,
`d0=33`, and the second helper's returned `a0` in `d1`. Preservation of the
earlier receiver and helper result through intervening calls is not established.

Construction saves its inputs, calls a helper, writes a literal word through
returned `a0`, and requests 172 bytes. Its `beq` at source `0x005d267a` skips
only the call to source `0x005d47d4` when the returned pointer is zero. Both
arms call local `0x6ebd26c6`, load the current pointer through `a2`, and reach
the writer at source `0x005d268f`. That leaf writes current `a1` and `d1` to
receiver fields `+152` and `+148`; `cmp 0,d0` / `beq` skips the `+144` write
on zero. The earlier guard does not establish null safety at this writer.

The action next requests 32 bytes and conditionally prepares an argument for
the dynamic-call body. That body saves its carrier `a0` at `sp+4`; null `a1`
returns `-268435434`. Otherwise it calls slot `+16`, saves returned `a0` in
`a3`, and uses that receiver for slots `+140` and `+144`, subject to intervening
call effects. The slot-`+144` result is saved in `d2`: `cmp 0,d2` / `bne`
at source `0x0059a168` skips the reloaded carrier's slot-`+20` call on nonzero.
Both arms reload the saved carrier and write 1 to its field `+20` at
`0x0059a179`. The subsequent slot-`+148` call uses current `a3`, initially
the slot-`+16` result, rather than that reloaded carrier. These receiver roles
must not be equated; preservation through the dynamic calls remains unproved.

Back in the action, `cmp 0,d2` / `bne` at source `0x005c9ea5` skips the state
helper on nonzero. The zero arm calls a helper that writes byte 1 to
`0x60358db4`, calls two further helpers, then writes byte 0. The action later
calls local `0x6ebd2694` with current `a3` in `a0` and returns current `d2`.
Neither the temporary
state writes nor the scalar return establishes exposure or an image owner.

**Next evidence:** [Resolve the release-control body's indirect
consumers](../RESEARCH.md#r-release-contract).

<a id="caller-record"></a>
## Caller record and scalar consumer

The body at source `0x005cbbe6` writes a record through addresses derived from
`d3`, initially supplied in `a1`, and uses some fields in a scalar calculation.
The output contains narrowed halfwords, bounded scalar choices, and full-width
copies whose types are unresolved. None identifies an image buffer or payload.

| Role | Local address | Block | Offset | Length |
|---|---|---:|---|---:|
| Caller | `0x6eb8d893` | 0 | `0x0058d8b3` | 101 |
| Record-writing body | `0x6ebcbbc6` | 0 | `0x005cbbe6` | 2871 |
| Scalar consumer | `0x6ebbee53` | 0 | `0x005bee73` | 60 |

These ranges and their selected canonical instructions use local code view
`source + 0x6e5fffe0`. The caller initially saves `a0` in `a3` and `a1` in
`a2`. After several calls, it moves current `a3` to `a0` and invokes wrapper
`0x6eb8cc42`. It then moves current `a2` to `a1` and calls the record body at
source `0x0058d8fb`, using the wrapper-returned `a0`. Complete preservation of
the original receiver and destination through those calls is not established.

At entry, `mov a1,d3` / `cmp 0,d3` / `bne` rejects a null destination with
`-268435434`. The next check loads receiver field `+20`: `cmp 0,d0` at source
`0x005cbbf8`, local `0x6ebcbbd8`, branches on nonzero to the continuation;
zero returns `-268435368`. The receiver itself has no preceding null check.
The body obtains another object in `a2` through local `0x6eb917e0`, then calls
two more helpers before reading its fields. The first output stores at sources
`0x005cbc34` and `0x005cbc3f` narrow current source words to destination
halfwords `+0` and `+2`. Subsequent branches constrain some output choices;
other stores copy full-width members without establishing their types.
The extended flow is reproduced from the range, not a complete canonical
instruction listing. Record identity and source-object preservation through
helpers remain qualifications on these field relationships.

At source `0x005cc2bf..0x005cc2c9`, current values from saved field addresses
and `a3` define `d0`, `d1`, and `a0` for the scalar consumer. Its entry saves
these in `d3`, `a2`, and `a3`. After a helper call it selects arithmetic
alternatives `47+d3`, `5+a2`, or `a3+1`: `cmp 0,d3` / `bne` at source
`0x005bee8a` keeps the first on nonzero; otherwise `cmp 0,a2` / `bne` at
`0x005bee92` keeps the second on nonzero, with the third on fallthrough.
After another helper it returns current `d2`. The record body sets
`a2=24` before this call, whose return restores `a2` and `d3`, then adds
current `d3` and stores returned `d0` at source `0x005cc2d2`. The helper calls'
effects on the scalar inputs and result still need verification.

The later `btst 4,d0` on global `0x6064c4e4` branches to local `0x6ebcc2cc`
when nonzero. Otherwise local `0x6eb90fde` is called; return 1 selects that
same continuation, while other values jump to the normal epilogue at source
`0x005cc719`. That epilogue clears `d0` and returns. This zero return, the
scalar field, and the unknown full-width members do not establish image
creation, ownership, lifetime, or host transfer.

**Next evidence:** [Identify the caller record's owner and
consumers](../RESEARCH.md#r-caller-record).

<a id="constructed-service"></a>
## Constructed service and receiver selection

A cached service stores an accessor result in field `+8`, then dispatches a
scalar and object argument through a selected receiver. On a valid cached-root
path, the accessor supplies the root's `+1868` subobject, not its separately
constructed `+128` subobject. The selected receiver and method effect remain
unresolved; this is not an established host request or capture interface.

| Role | Block | Offset | Length |
|---|---:|---|---:|
| Service factory | 0 | `0x007eede0` | 48 |
| Service constructor | 0 | `0x007eee10` | 34 |
| Dispatch body | 0 | `0x007eee99` | 27 |
| Root accessor | 0 | `0x007eeed2` | 59 |
| Root constructor | 0 | `0x007eef39` | 192 |
| Subobject getter | 0 | `0x007ef08c` | 7 |
| Root aggregate check | 0 | `0x007ef0d6` | 81 |
| Receiver selector | 0 | `0x007eea1b` | 36 |
| +1868 constructor | 0 | `0x007efc1a` | 134 |
| Its base constructor | 0 | `0x007ed056` | 44 |
| +128 constructor | 0 | `0x007f17e3` | 108 |
| Its base constructor | 0 | `0x007eaf27` | 95 |
| Candidate table suffix | 0 | `0x008f7560` | 24 |

The recorded code view is `source + 0x6e5fffe0`; branch targets below use
source offsets to avoid confusing them with the recorded CODE addresses.
Data placement does not follow automatically from this code view. The table
suffix has range-only support, not a canonical instruction listing or proven
connection to the installed service table.

The factory tests global `0x6035afd4`, requests 12 bytes on zero, and skips
construction when the allocation result is zero. Both paths store current
`a0` and return the reloaded global. The constructor calls source `0x007f277f`,
uses its returned `a0` as the service base, installs literal `0x6eef8980`,
clears field `+8`, and fills it with the root accessor's return. Preservation
of the saved input through the factory's allocation remains a qualification.

The root accessor tests `0x6035afd8`, requests 2644 bytes on zero, conditionally
constructs the root, stores current `a0`, and calls the aggregate check on that
arm. It then reloads the cached root and calls the getter. The getter
unconditionally adds 1868; a zero cached root does not produce a safe null
return. The aggregate check calls separate subobject checks and ANDs current
results, with intervening register effects still requiring verification.

The root constructor saves the base helper's returned `a0` in `a2` and installs
`0x6eef8998`, distinct from the service literal. Source `0x007eef54` calls the
`+128` constructor at `0x007f17e3`; source `0x007eef81` calls the `+1868`
constructor at `0x007efc1a`. It also constructs objects at `+460`, `+880`,
`+2180`, and `+2204`. These expressions use current saved registers: equality
to the original root across intervening calls is not implied by field layout.
The `+1868` constructor installs `0x6eef8af8` through its base constructor's
return; the `+128` constructor installs `0x6eef8d90` through its own base
return. The latter base directly clears its current owner's field `+140`.
The selected `+1868`/base bodies contain no direct `+140` store. That absence
establishes neither initializedness nor that all possible producers lie behind
an indirect slot.

The selector reads current receiver field `+140`. At source `0x007eea21`,
`cmp a2,d0` / `beq` selects `0x007eea29` when it equals the saved receiver;
the following zero test also falls through to that load for zero. That arm
returns the field itself, including zero. A different nonzero field reaches
`0x007eea2d` and calls its table slot `+156`. A nonzero returned `a0` exits
at `0x007eea3c`; zero falls through to `mov a2,a0` at `0x007eea3b`, using
current saved `a2`. Preservation across the indirect call remains necessary.

The dispatch body loads service field `+8`, saves incoming `d0` in `d2` and
`a1` in `a2`, and calls the selector. It then forwards current `d2` as `d0`
and restored `a2` as `a1`, dereferences the returned receiver's table, and
calls slot `+4` without a null guard. The selector restores `a2`, but its
indirect arm does not establish `d2` preservation; its `[a2]` return mask alone
cannot justify calling the forwarded scalar the original request. The dispatch
epilogue restores its caller's `d2` and `a2` separately from those arguments.

**Unresolved:** runtime table placement/selection, allocation and current-pointer
validity, transitive preservation, field `+140` production, and the selected
receiver's effect and lifetime. Neither construction nor this indirect call
identifies still capture, an image owner, or host transfer.

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
