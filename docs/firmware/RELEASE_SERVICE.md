# Constructed release service and conditional endpoint

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open questions](../RESEARCH.md)

A constructed service selects a receiver through a cached root; a conditional
table interpretation nominates an endpoint with separate object arguments.
The detailed contracts below distinguish construction identity from later
storage effects and live selection. Neither relationship establishes capture.
See [release-control candidates](RELEASE_CONTROL.md) for other entry points.

- [Constructed service and receiver selection](#constructed-service)
  - [Service allocation and cached root](#service-allocation-and-cached-root)
  - [Construction identity and initial fields](#construction-identity-and-initial-fields)
  - [Owner preservation through the base chain](#owner-preservation-through-the-base-chain)
  - [Pointed-storage effects and later wiring](#pointed-storage-effects-and-later-wiring)
  - [Receiver selection and dispatch arguments](#receiver-selection-and-dispatch-arguments)
- [Conditional receiver-table endpoint](#conditional-receiver-endpoint)
  - [Endpoint arguments and branch outcomes](#endpoint-arguments-and-branch-outcomes)
  - [Native records and the shared continuation](#native-records-and-the-shared-continuation)

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
| Root's +2180 helper | 0 | `0x007f271e` | 15 |
| Its nested helper | 0 | `0x007eb634` | 14 |
| Subobject getter | 0 | `0x007ef08c` | 7 |
| Root aggregate check | 0 | `0x007ef0d6` | 81 |
| Receiver selector | 0 | `0x007eea1b` | 36 |
| +1868 constructor | 0 | `0x007efc1a` | 134 |
| Its base constructor | 0 | `0x007ed056` | 44 |
| Directly selected base setup | 0 | `0x007ee993` | 72 |
| First pointed-storage setup helper | 0 | `0x007ec885` | 47 |
| Root wiring | 0 | `0x007ef127` | 97 |
| Current receiver +272 setter | 0 | `0x007f02dd` | 7 |
| Current receiver +276 setter | 0 | `0x007f02eb` | 7 |
| +128 constructor | 0 | `0x007f17e3` | 108 |
| Its base constructor | 0 | `0x007eaf27` | 95 |
| Candidate table suffix | 0 | `0x008f7560` | 24 |

The recorded code view is `source + 0x6e5fffe0`; branch targets below use
source offsets to avoid confusing them with the recorded CODE addresses.
Data placement does not follow automatically from this code view. The table
suffix has range-only support, not a canonical instruction listing or proven
connection to the installed service table.

### Service allocation and cached root

The factory tests global `0x6035afd4`, requests 12 bytes on zero, and skips
construction when the allocation result is zero. Both paths store current
`a0` and return the reloaded global. The constructor calls source `0x007f277f`,
uses its returned `a0` as the service base, installs literal `0x6eef8980`,
clears field `+8`, and fills it with the root accessor's return. Preservation
of the saved input through the factory's allocation remains a qualification.

The root accessor tests `0x6035afd8` and requests 2644 bytes on zero. After
saving the allocation result in `a2` and setting `a0=0`, source `0x007eeeea`
compares `a0,a2`; `beq` at `0x007eeeeb` takes zero to `0x007eeef4`, skipping
construction. Nonzero falls through to argument setup at `0x007eeeed` /
`0x007eeeee` and the constructor call at `0x007eeeef`. Source `0x007eeef4`
stores current `a0` into the cache, then calls the aggregate check without a
new null guard. On a valid nonzero normally returning construction path, the
root-owner contract below identifies this stored pointer as returned `R`.

This cache **store** is distinct from the later reload at `0x007eeeff` after
the aggregate. The aggregate calls separate subobject checks, ANDs current
results, and directly calls source `0x0081c252` at `0x007ef11b`. Its scalar
result does not establish absence of indirect global-state effects. Relating
the later cached pointer to the earlier stored `R` requires those effects to
be resolved. The getter unconditionally adds 1868; a zero cached root does
not produce a safe null return. Allocation validity, lifetime and intervening
register effects remain separate obligations.

### Construction identity and initial fields

The root constructor saves the base helper's returned `a0` in `a2` and installs
`0x6eef8998`, distinct from the service literal. Source `0x007eef54` calls the
`+128` constructor at `0x007f17e3`; source `0x007eef81` calls the `+1868`
constructor at `0x007efc1a`. It also constructs objects at `+460`, `+880`,
`+2180`, and `+2204`. Expressions using other current registers still need
their actual preservation contracts; field layout alone is not an identity
proof. The saved-root `a2` itself survives the required root calls: complete
source `0x007f271e` calls complete `0x007eb634`, whose nested source
`0x005968da` call lists `[a2,a3]`, with no local writes to those registers in
either wrapper. Their writes through current returned `a0` do not identify
that pointer with the original `R + 2180` storage. The root's other selected
calls list `a2` in their masks. Consequently source `0x007eeff5` copies saved
root `R` to `a0` before `ret [d2,d3,a2,a3],32` at `0x007eeff6`, on the valid
normally returning path. This proves conditional constructor-return/cache-store
identity, not an immutable cache or preservation of every internal `a3`/`d3`
expression. Restoring the caller's registers at the final return is distinct
from preserving the constructor's internal values across each call.
The `+1868` constructor installs `0x6eef8af8` through its base constructor's
return; the `+128` constructor installs `0x6eef8d90` through its own base
return. The latter base directly clears its current owner's field `+140`.

On the valid, normally returning construction path, the object receiving the
`+1868` constructor's `0x6eef8af8` installation is also the object whose
`+140` and `+144` are initially cleared by direct base setup. Call that object
`B0`. At root call source `0x007eef81`, it is current saved root `R + 1868`:
the root's preceding selected calls list `a2` in their preservation masks,
and source `0x007eef79..0x007eef7e` forms that argument from saved `a2`.
This partial owner join does not establish the final `+1868` constructor return,
the later cached-root reload's identity, later field value, or runtime selection.

| Owner-contract support | Block | Offset | Length |
|---|---:|---|---:|
| Common-base stack-argument prefix | 0 | `0x0081bd5a` | 2 |
| Common-base owner continuation | 0 | `0x0081bd5c` | 97 |
| Intermediate base | 0 | `0x007ecb2f` | 59 |
| Its clear-only tail | 0 | `0x007ecf84` | 12 |
| Direct setup clear-only tail | 0 | `0x007eeaba` | 12 |
| Outer base clear-only tail | 0 | `0x007ed312` | 12 |
| +1868 constructor clear-only tail | 0 | `0x007f02fd` | 44 |
| Current a0 +12 writer | 0 | `0x00819dc6` | 6 |

### Owner preservation through the base chain

Common base source `0x0081bd5a` stores entering `a1` on the stack, then
`0x0081bd5c` saves entering `a0` in `a2`. Its selected calls preserve `a2`;
the final unmasked source `0x00819dc6` only stores current `d0` through current
`a0 + 12` and returns without writing the owner register. Source
`0x0081bdb9` copies saved `a2` to `a0` before the return. The call at source
`0x0081bdac` selects source `0x0081c1ba`: its canonical alternate display
view is `source + 0x402bffe0`, while the caller's CODE-local target is
`0x6ee1c19a`. Neither display arithmetic is the separate DATA view.

Intermediate base `0x007ecb2f` saves that returned owner in `a2`, preserves it
around its listed-mask calls, and restores it after the complete unmasked
`0x007ecf84` tail, which clears only `+132`/`+136` without owner-register
writes. This intermediate base stores **-1**, not zero, at current owner's
`+128` (`0x007ecb50` / `0x007ecb52`). Direct setup `0x007ee993` saves the
same returned `B0`, installs its literal, clears `d0`, and writes zero to
`B0 + 140` / `B0 + 144` at `0x007ee9a4` / `0x007ee9a8`. It calls source
`0x007ec885` with `B0 + 148`, `B0 + 168`, and `B0 + 188`, preserving saved
`a2` around each call and source `0x0081c176`. The copies at `0x007ee9c7`,
`0x007ee9d1`, and `0x007ee9d7` are `mov a2,a0`, not helper-return rebindings.
Its complete `0x007eeaba` tail and outer base's complete `0x007ed312` tail
clear only `+208`/`+212` without owner-register writes. Their saved-owner
copies and returns therefore supply `B0` to `0x007efc23`, which saves it in
`a3` before literal installation at `0x007efc2a`.

### Pointed-storage effects and later wiring

Owner-register preservation does not prove pointed-storage preservation. The
first subsequent storage dependency is `0x007ec885` at `0x007ee9b0` with
`B0 + 148`; its allocator and the other direct/indirect effects have not been
shown to leave `B0 + 140` unchanged. Define `U=B0+148` for that first helper:
it saves entering `a0` as `a3`, sets local `a2=U+4`, and writes fields at
`U`, `U+4`, `U+8`, `U+12`, and `U+16` before its allocator call at
`0x007ec8a7`. These are U-relative fields, not `B0+4..+16`. The size formation
is 20 shifted left twice (80 bytes). Its post-call store uses current `a2`,
and its natural return at `0x007ec8b0` copies current `a3` to `a0`; the
allocator's pointed-storage, returned-pointer validity and relevant register
effects must be established rather than inferred from an empty mask.
Likewise the `+1868` constructor's first allocator size is 80, but its second
size formation uses current `d3` after the first helper; it is not proved to
remain the original 20. Later constructor calls to
`0x0081bc3b` at `0x007efc57` / `0x007efc79` also require their actual storage
and register contracts. An empty mask alone proves neither clobber nor
preservation. The final `0x007f02fd` tail has no owner-register write or
`+140` store: it clears current `+208`, `+212`, and `+280..+308` in four-byte
steps and returns at `0x007f0326`. It does not repair an earlier unknown
effect. The copies at `0x007efc8d` / `0x007efc9c` are `mov a3,a0`, not
rebindings of saved `a3` from helper returns.

Root source `0x007eefe7` explicitly copies current saved `a2` to `a0` before
calling wiring source `0x007ef127`, whose first instruction defines its own
`a3` from incoming `a0`. Its initial `d2` formation is that current root plus
1868. Calls at `0x007ef134` and `0x007ef140` select the complete leaves
`0x007f02dd` and `0x007f02eb`, writing entering `a1` to current receiver
`+272` and `+276`. Other calls select the `+160` setter at source
`0x007eb22f`, covered by canonical range `[0x007eb216,0x007eb242)`.
Those leaves write their stated fields, not `+140`. Relating every later wiring
expression to the original allocated root still requires the intervening
helper contracts; an empty mask alone proves neither clobbering nor preservation.

### Receiver selection and dispatch arguments

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

**Next evidence:** [Live service receiver and method](../RESEARCH.md#r-release-service).

<a id="conditional-receiver-endpoint"></a>
## Conditional receiver-table endpoint

A range-only table anchor nominates a wrapper that forwards three entering
arguments to further object dispatch. Its first branch depends on a loaded
global, not the entering scalar. Neither the table relation nor the endpoint's
normal return establishes stock receiver selection or a capture effect.

| Role | Block | Offset | Length |
|---|---:|---|---:|
| Conditional installed-table prefix | 0 | `0x008f76d8` | 8 |
| Conditional table slot +52 | 0 | `0x008f770c` | 4 |
| Conditional table slot +64 | 0 | `0x008f7718` | 4 |
| Conditional table slots +72/+76 | 0 | `0x008f7720` | 8 |
| Wrapper entry and direct call | 0 | `0x007eccbf` | 12 |
| Overlapping call-through-return span | 0 | `0x007eccc4` | 32 |
| Direct endpoint | 0 | `0x0081c0ec` | 71 |
| Shared continuation | 0 | `0x0081c73b` | 103 |

Under the separately conditional DATA-local `source + 0x6e601420` view,
installed literal `0x6eef8af8` nominates source `0x008f76d8`. Its `+4` word
at `0x008f76dc` is `0x6edee0df`, nominating source `0x007eccbf` under that
same view. This arithmetic does not prove runtime data placement, a live
installed table, or selection through current `+140` / slot `+156`.
The two overlapping wrapper ranges cover `[0x007eccbf,0x007ecce4)`; a complete
source-anchored replay shows its direct call to `0x0081c0ec` at
`0x007eccc4` without preceding overwrites of entering `a0`, `a1`, or `d0`.
No new wrapper or endpoint instruction rows are implied by the table range.

Under the same conditional DATA view, source `0x008f7718` holds
`0x6ee1d263`, nominating `0x0081be43` as slot `+64`; source
`0x008f7720` / `0x008f7724` hold `0x6ee1d38f` / `0x6ee1d39e`, nominating
`0x0081bf6f` / `0x0081bf7e` as slots `+72` / `+76`. These are the same code
profiles reviewed in the [still-corridor continuations](STILL_OBJECTS.md#continuations),
not proof that the E table and that corridor's parent table or objects are
identical. The complete native `+72` profile forwards entering `a0/a1/d0`
to the receiver's `+64` method; native `+64` and `+76` form their specified
stack records on the stated arms rather than requiring an externally guessed
layout. Their argument formation is a partial source-level input join only.

Source `0x008f770c` holds slot-`+52` word `0x6ee1dc28`, nominating
the six-byte getter at source `0x0081c808` under this same conditional DATA
view. It loads current receiver `+100` into `a0` without other register or
data-memory writes. Together with the direct predicate, this supports the
[gate-clear E/Q argument join](STILL_OBJECTS.md#continuations) up to the
Q-table `+40` call, conditional on valid entering objects and the selected
table. It does not identify the loaded pointer as an image.

### Endpoint arguments and branch outcomes

The following role names apply only to this endpoint; they are not recovered
types or identities shared with another finding.

| Role | Entry register | Meaning here |
|---|---|---|
| E | `a0` | Entering endpoint receiver |
| P | `d0` | Entering argument, used as a pointer on the nonzero-global arm |
| Q | `a1` | Entering object argument |

Source `0x0081c0ec` saves `E` in `a3`,
`0x0081c0ed` saves `P` in `a2`, and `0x0081c0f5` saves `Q` at `sp+4`.
Source `0x0081c0ef` **loads** global `0x6035b1ac` into `d0`; it does not
store `P`. The compare at `0x0081c0f7` and `bne` at `0x0081c0f9` select
`0x0081c104` when that global is nonzero. Zero falls through, restores saved
`P` into `d0`, calls `0x0081c73b [d2,d3,a2,a3],24`, then branches to the
sole `ret [a2,a3],16` at `0x0081c130`. Thus `P=0` does not select the
zero-global arm or establish null safety; `P` can be nonzero on that arm.

The nonzero-global arm consumes entering `P` as a pointer and calls its table
slot `+12` at `0x0081c10a`. Source `0x0081c10c` copies current returned `a0`
to `d0`, compares it with zero at `0x0081c10e`, and `beq` at `0x0081c110`
takes zero to `0x0081c11e`. Nonzero reloads the stack argument, calls current
E-table slot `+76`, and branches directly to the return at `0x0081c11c`;
it does not also call slot `+72`. Zero instead uses current `a2` for P-table
slot `+4`, reloads the stack argument, and calls current E-table slot `+72`.
The indirect calls are unmasked: later `a2`/`a3` identities require their
actual contracts, while the stack reload is explicit. Pointer-used `P` is not
a proved numeric opcode, image class, or payload owner.

The nonzero table-`+12` result is still current `d0` at the `+76` call; its
native wrapper copies that entering `d0` to `d1` before normalizing it. On the
other arm, the later `+72` input is current `d0` after P-table `+4`, not a
proved conventional status/opcode or preserved entering argument. Native
record initialization, scalar return and reset are not operation-completion
or image-ownership proofs.

### Native records and the shared continuation

Under the separately conditional [native record-table assignment](STILL_OBJECTS.md#continuations),
P-table `+12` reads current `P+8` into `a0`; the explicit copy at
`0x0081c10c` makes that value the endpoint's tested `d0`. P-table `+4`
reads current `P+4` into `d0`. Initial field values cannot be propagated
through unproved storage effects. The native `+64/+76` bodies directly
call `0x0081c73b`, without calling this endpoint or testing its first global.
A nonzero global here can also dispatch to those bodies through E-table
`+72/+76`; it does not exclude all entry to the shared continuation.
An equivalent record supplied to this endpoint remains a hypothetical input
contract rather than a source-proven native-producer/endpoint chain.

The [shared continuation](STILL_OBJECTS.md#continuations) has its own optional
object call and compares a later global load with **current** `d2`, not a
proved preserved zero. Neither complete endpoint body directly writes global
`0x6035b1ac`; their indirect methods' global and object effects remain open.
Shared code does not identify this E table with the still corridor's separate
parent table or its field-`+100` object.

**Unresolved:** actual table/receiver selection, valid live `E/P/Q` objects and
their lifetime, argument/register/storage preservation beyond the qualified
gate-clear join, indirect method effects, and host ingress. Native stack
lifetime during the call does
not establish that an endpoint cannot retain the record or that literal
`0x6eeffee4` identifies a valid live table. An explicit-receiver adapter could
bypass a selector or use native record formation conceptually, but would not
manufacture those contracts. Numeric
argument 33, forced-null safety, capture, image ownership, transfer, device
acceptance, and patch safety are not established.

**Next evidence:** [Endpoint objects and effects](../RESEARCH.md#r-release-endpoint), keeping the global-state branch
distinct from the `P` pointer and its table-`+12` return.
