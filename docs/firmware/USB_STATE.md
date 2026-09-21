# USB state reporting and candidate byte stores

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open questions](../RESEARCH.md)

These separate static paths report values or read and write candidate state bytes.
Their live owners, numeric meanings, and connection to shooting remain unresolved.
For the selected query provider see [USB policy](USB_POLICY.md); for measured
personality and session behavior see [USB observations](../observations/USB_AND_MEDIA.md).

- [Named USB-state reporting wrapper](#usb-state-wrapper)
- [Candidate connection callback, byte stores, and consumer](#usb-connect-stores)

<a id="usb-state-wrapper"></a>
## Named USB-state reporting wrapper

The source-selected body associated with `getUsbState` reports labels for two
current-register values and clears `d0` before normal return. Its name does not
establish a caller-visible numeric USB-state getter or a live connection state.

| Role | Block | Offset | Length |
|---|---:|---|---:|
| Source-selected wrapper | 0 | `0x005de67b` | 76 |
| Method name | 0 | `0x0086bb10` | 12 |
| Three-word row | 0 | `0x0086e5c0` | 12 |
| Zero-branch label | 0 | `0x008722ce` | 14 |
| One-branch label | 0 | `0x008722dc` | 17 |

The row contains pointer literals `0x6ee6cf30`, `0x6ebdfa9b`, and
`0x6ee6cf3c`. Under the conditional DATA-local view `source + 0x6e601420`,
the first selects the name and the second selects the wrapper. This coherent
view is not runtime placement or a universal code/data mapping; the third
word's role is unresolved. The two branch labels are `API_CONNECTED` and
`API_DISCONENCTED` (source spelling). They do not establish an enum domain or
actual USB personality, session ownership, or connection.

The wrapper's 21 canonical instructions use local view
`0x6ebdfa9b..0x6ebdfae7`. They leave a two-byte gap at source `0x005de68c`;
the 76-byte authenticated range is not a complete canonical instruction listing.
Source `0x005de680` calls local `0x6eb82317`, then loads `(a0)` into `a1`
and slot `+40` into `a1`. The accessor, installed table, and selected slot-40
body are source-joined in the [transition-policy finding](USB_POLICY.md#pc-usb-transition).
That static join does not establish live singleton selection or lifetime.
After the gap, source `0x005de68e` copies current `d0` into `d2`.

Source `0x005de68f` defines `d0=65801` before the call at `0x005de695`
to local `0x6eb97e18,[d2],4`. Source `0x005de69c` copies current `d2`
into `d0` before `0x005de69d` calls `0x6eb80db8,[d2,a2,a3],28`.
The encoded masks alone do not prove either reporting callee's saved-stack,
return, or register-preservation contract. The later comparisons therefore
refer to current `d2`, conditionally related to the earlier copied value.

At `0x005de6a4`, `cmp 0,d2` and the following `beq` take zero to
`0x005de6ae`, which selects pointer `0x6ee737ee` for `API_CONNECTED`.
Otherwise `cmp 1,d2` at `0x005de6a8` and its `beq` take one to
`0x005de6b6`, selecting `0x6ee737fc` for `API_DISCONENCTED`.
Both selections join the reporting call at `0x005de6bc` to
`0x6eb80d74,[a2,a3],20`; other current `d2` values branch directly to
`0x005de6c3`. All normal paths through this selected body join `clr d0`
at `0x005de6c3` and the complete `ret [d2],8` at `0x005de6c4`.

The slot-40 source chain produces a normalized lower-provider result, but the
provider's owner, live value production, object lifetime, synchronization, and
this wrapper's reporting preservation contracts remain unjoined. This does not
identify shooting restrictions, capture initiation, image association, or host
transfer.
See [State owner and reporting contract](../RESEARCH.md#r-usb-state-owner) and the
separate [historical session observations](../observations/USB_AND_MEDIA.md#personalities).

<a id="usb-connect-stores"></a>
## Candidate connection callback, byte stores, and consumer

The candidate body at source `0x00acfa9b` selects two sets of explicit
one-byte writes through four direct-call leaves. It is not merely a reporting
wrapper. Its proposed USB-connect role does not establish live registration,
the meaning of the numeric states, or a shooting-state consumer.

The 78 canonical instructions completely cover block-0 source body
`[0x00acfa9b,0x00acfb69)` (206 bytes) and four nine-byte leaves at
`0x00acf958`, `0x00acf96a`, `0x00acf97c`, and `0x00acfa89`.
These are instruction coordinates, not canonical range rows. Their CODE-local
view is `source + 0x6e5fffe0`: body entry `0x6f0cfa7b` and leaves
`0x6f0cf938`, `0x6f0cf94a`, `0x6f0cf95c`, and `0x6f0cfa69`.
This local arithmetic does not prove runtime placement or a DATA mapping.

Entry copies are source `0x00acfaa0:d1->d2`, `0x00acfaa1:d0->d3`, and
`0x00acfaa2:a1->a2`. Initialization at `0x00acfaab` and reporting at
`0x00acfac5` intervene before the comparisons. Their encoded call masks do not
establish original-input preservation or a callback ABI; conditions below
refer to current `d3` and `d2` at the tests.

Source `0x00acfacc` compares `16,d3`; `beq` at `0x00acface` selects
`0x00acfad3`, while fallthrough returns at `0x00acfad0`. The selected chain
compares current `d2` with 3, 72, 71, and 70 at `0x00acfad3`,
`0x00acfad7`, `0x00acfadb`, and `0x00acfadf`. Taken branches at
`0x00acfad5`, `0x00acfad9`, `0x00acfadd`, and `0x00acfae1` select
the corresponding arms; an unmatched value returns at `0x00acfae3`.

| Current test values | Selected arm | Explicit byte writes, in order | Return |
|---|---|---|---|
| `d3==16`, `d2==3` | `0x00acfae6`; opaque call at `0x00acfaed` | None in the selected caller arm | `0x00acfaf4` |
| `d3==16`, `d2==72` | `0x00acfaf7`; opaque call at `0x00acfb03` precedes stores | `0x60353190=1`, `0x60353191=4`, `0x60353192=0` | `0x00acfb66` |
| `d3==16`, `d2==71` or `70` | `0x00acfb39` | `0x60353193=5`, `0x60353190=11`, `0x60353191=2` | `0x00acfb66` |

Each store argument is immediately defined in `d0` before its direct call:
sources `0x00acfb0a/0c`, `0x00acfb11/13`, `0x00acfb18/19`,
`0x00acfb39/3b`, `0x00acfb40/42`, and `0x00acfb47/49`.
The leaves contain complete six-byte `movbu d0,(address)` followed by
three-byte `retf [],0`. The two store arms perform further opaque calls;
the 72 arm branches from `0x00acfb37` to the shared return. All four return
sites have identical complete three-byte `ret [d2,d3,a2,a3],44`; not every
path reaches the final site.

These writes are conditional normal-execution effects, not proof of persistent
global values. Opaque helper effects, address validity, lifetime, and later or
concurrent changes remain unresolved; no-store arms do not prove unchanged
state. There is no established join to the named wrapper's slot-40 value.

A separate dispatcher and consumer read the same candidate-state storage. The
151 canonical instructions completely cover dispatcher
`[0x00acf65e,0x00acf691)`, consumer `[0x00acf74a,0x00acf83e)`, helper
`[0x00acf86b,0x00acf8b1)`, and getter `[0x00acf985,0x00acf98e)` under the
same conditional CODE-local `source + 0x6e5fffe0` view. The dispatcher calls
the consumer at source `0x00acf67b` when its current `d0` equals 4. This is a
source-level selection, not proof that the dispatcher is entered or that 4
denotes a live USB state.

The consumer initializes stack bytes `sp+4=1` and `sp+5=4`, calls the getter,
saves its returned `d0` in `d2`, and calls the 1,580-byte-frame helper. The
getter directly loads unsigned byte `0x60353192` and returns. Subsequent tests
use current post-helper `d2` and the low halfword of current `d0`; the encoded
call/return masks do not prove that they preserve the pre-helper values.

| Current post-helper values | Explicit branch-local effects before the shared tail |
|---|---|
| `d2=0`, `d0=0/1/2` | Call arguments `(d0,d1)=(14,13)`, `(14,14)`, or `(14,15)` to `0x6f09ad39` |
| `d2=0`, `d0=3` | Two opaque calls precede a current-`d0==1` split; equality selects another opaque call and a call with `d0=11`, while inequality selects `(14,17)` for `0x6f09ad39` |
| `d2=1`, `d0=0` | Store 36 through the existing `0x60353193` leaf, write stack bytes 0/2, then select `(14,17)` |
| `d2=1`, `d0=1` | Write stack bytes 0/0, store 2 through the `0x60353192` leaf, then call `0x6f0cf3fe` with `d0=2` and current saved consumer object in `a0` |
| `d2=2`, `d0=0` | Write stack bytes 0/0, then call `0x6f0cf96e` with pointers to those two stack bytes |
| `d2=2`, `d0=1` | Write stack bytes 0/0, store 3 through the `0x60353192` leaf, then call `0x6f0cf3fe` with `d0=3` and current saved consumer object in `a0` |

All other tested values reach the shared tail without those listed
branch-local effects. The tail reloads the **current** stack bytes and calls
the existing setters for `0x60353190` and `0x60353191`; intervening opaque
calls can change those bytes, globals, and receiver registers. In the helper,
the byte-derived `d3` calculation occurs before an opaque initializer call, so
the later table-address calculation uses current post-call `d3`. Its scratch
storage, table validity, loop termination, returned scalar, and preservation
effects remain unresolved.

The numeric states, calls, and byte stores do not identify connected versus
disconnected, Storage/MTP, shooting permission, capture, image ownership, host
transfer, or a safe mode override. They also do not connect this consumer to
the named wrapper's slot-40 value.

**Next evidence:** [Candidate state owner and meaning](../RESEARCH.md#r-usb-state-owner).
