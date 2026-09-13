# Live-view objects and ThroughImage selector

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open
questions](../RESEARCH.md)

The mapped lifecycle and collection operations describe object management. The
ThroughImage path returns a scalar obtained through a record lookup. Neither
path yet identifies a frame-buffer owner or an image payload.

- [Singleton lifecycle](#lifecycle)
- [Collection, tables, and temporary copies](#collections)
- [ThroughImage receiver and scalar lookup](#throughimage)
- [Separate initializer and the missing record connection](#record-initializer)

<a id="lifecycle"></a>
## Singleton lifecycle

The corridor beginning at `0x40ab9dbd` (`block 0`, offset `0x007f9ddd`) is a
reverse-order destructor, not a constructor. A direct call at `0x40ab9e73`
targets `0x40aba041`. The authenticated containing span is:

```text
block=0 offset=0x007f9ddd length=382
sha256=592f4b119e2fa9efc4a4b68db11331e49a85530860a935faed3ba833eb965449
```

At `0x40aba041`, the canonical `mov 1861203104,d0` is backed by block 0,
offset `0x007fa061`, length 6.

The lazy singleton accessor is at `0x40ab9cbd`; its construction path begins
at `0x40ab9ceb`, spans 468 bytes, and has eight authenticated direct callers.
The accepted evidence still does not identify a frame-buffer owner, pixel
format, or display/export consumer.

**Next evidence:** [Identify the live-view frame
owner](../RESEARCH.md#r-live-view-owner).

<a id="collections"></a>
## Collection, tables, and temporary copies

The singleton constructor binds `root+52 = root+276`; the embedded object at
`root+276` receives dispatch word `0x6eef8128`; and the transfer at
`0x40aba1aa` is mechanically `calls *(*(root+52))`. A separate relationship
copies the collection at `outer+132` into `outer+24` and an alias at
`(outer+248)+24`; wrapper `0x40aba091` passes `outer+24` to collection routine
`0x40aac8b4`, which can append the pointer to a dynamic array.

Runtime dispatch table `0x6eefb4a0` is mapped to block-0 offset `0x008fa080`;
slot `+0x10` resolves to wrapper `0x40aba091`, closing one table edge in the
collection path. The 16-slot table at runtime `0x6eef8128` is authenticated at
block-0 offset `0x008f6d08`; slot `+0` conditionally resolves to `0x6edec9be`. A separate 55-entry pointer structure at runtime `0x6ee3e908` is
authenticated at block-0 offset `0x0083d4e8`. Which slot carries the
`outer+132` collection element, the identity between the provider and its
returned product, and any frame, display, DMA, or export effect remain
unresolved.

The `0x6ee3e908` table head has two bounded relationships. The helper at
`0x6eb7e2d8` stores that value through caller-supplied `a0`, clears the field
at `a0+8`, and returns zero. A separate path beginning with the call at
`0x40aac8d7` to `0x40aaca42` builds a 12-byte temporary with the same dispatch
value, copies two stack words into it, and copies three words to a
caller-provided destination. The destination owner and its relationship to the
live-view collection remain unresolved.

**Next evidence:** [Identify the live-view frame
owner](../RESEARCH.md#r-live-view-owner).

<a id="throughimage"></a>
## ThroughImage receiver and scalar lookup

The receiver selects a helper that returns a halfword-derived scalar. The
record array's contents and producer are unresolved.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Constructor-shaped body | `0x6edfc227` | 0 | `0x007fae07` | 79 |
| Installed table | `0x6eefbc84` | 0 | `0x008fa864` | 140 |
| Selector body | `0x6e868efe` | 0 | `0x00267ade` | 56 |
| Selector return | `0x6e868f36` | 0 | `0x00267b16` | 3 |
| Record-search helper | `0x6e76d553` | 0 | `0x0016c133` | 224 |

**Established relationships**

1. The constructor-shaped body installs `0x6eefbc84` through the incoming
   receiver, clears fields, initializes embedded objects at `+12` and `+48`,
   and returns the receiver. Table slot `+0x20` selects caller `0x6edfc346`,
   which supplies selector 4 to `0x6e868efe`, saves its result, and forwards
   the scalar in `d0`.
2. The selector maps 4 to `0x2100`, 5 to `0x2400`, and other values to
   `0x0c00`. It passes a stack halfword destination to `0x6e76d553`, clears
   that halfword on nonzero helper status, and loads it unsigned into `d0`.
   The canonical `ret [d2],12` at `0x6e868f36` completes the local span
   through `0x6e868f39`.
3. The helper searches 8-byte records from `0x6034aff0` by halfword key,
   using `0x2900` as the sentinel. Root loads at `0x6e76d58c` and
   `0x6e76d592` explicitly establish that base. A matching record's word at
   `+4` goes to `0x6e76efc8` and `0x6e76ee46`; the latter also receives
   the saved destination. The helper returns a halfword status.

**Unresolved:** the live records, the value selected for `0x2100`, downstream
callee effects, and runtime reachability. “ThroughImage” does not identify a
JPEG/frame owner, and the scalar result does not establish an image pointer.

**Next evidence:** [Find the producer of the ThroughImage
record](../RESEARCH.md#r-throughimage-record).

<a id="record-initializer"></a>
## Separate initializer and the missing record connection

An initializer uses the same key as the selector, but no supported connection
shows that it populates the selector's runtime array.

| Role | Local address / data value | Block | Offset | Length |
|---|---|---:|---|---:|
| Initializer-shaped caller | `0x6e76df43` | 0 | `0x0016cb23` | 51 |
| Receiver-field initializer | `0x6e76edd1` | 0 | `0x0016d9b1` | 75 |
| MENU_BG identifier | `source only` | 0 | `0x0036c8bf` | 8 |

**Established relationships**

The caller passes `0x2100` and a reference to `MENU_BG` to `0x6e76edd1`. The
canonical rows at `0x6e76edd2` and `0x6e76edd8` load `0x6e96def4` and store it
through `a2`.

The initializer saves incoming `a0` in `a2`, stores `d0` and `d1` at receiver
`+12` and `+16`, copies stack arguments to `+20`, `+22`, `+24`, `+28`, and
`+30`, and clears `+4` before an intervening call. Its trailing
`ret [d2,a2,a3],16` is canonical. The accepted range covers
`0x6e76edd1..0x6e76ee1c` / source `[0x0016d9b1,0x0016d9fc)`, including
intervening instructions not individually recorded in the corpus.

**Unresolved:** caller argument identities, register preservation across the
call, and whether these writes produce the live `0x2100` record's `+4` value in
`0x6034aff0`. The connection to queued-copy handoff `0x6e61fd8d` /
`0x6e68939a` also remains unproved. A matching key alone joins neither path.

**Next evidence:** [Find the producer of the ThroughImage
record](../RESEARCH.md#r-throughimage-record).
