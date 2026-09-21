# Communication state and USB event ownership

[Map](../FIRMWARE_MAP.md) · [Reading conventions](READING.md) · [Open questions](../RESEARCH.md)

A communication-state family has local connect/disconnect transitions and
opaque effect-bearing calls. Separate USB-labelled name maps supply a bounded
negative about event ownership. Neither establishes a host-controlled USB
cycle or selects the [named MTP lifecycle](MTP_LIFECYCLE.md).

- [Communication disconnect/connect state machine](#communication-cycle)
  - [State fields and diagnostic labels](#state-fields-and-diagnostic-labels)
  - [Disconnect input and receiver boundaries](#disconnect-input-and-receiver-boundaries)
  - [End-communication receiver and method](#end-communication-receiver-and-method)
  - [Connecting and protocol selection](#connecting-and-protocol-selection)
  - [USB-labelled name maps and lookup boundaries](#usb-disconnect-name-maps)

<a id="communication-cycle"></a>
## Communication disconnect/connect state machine

A separate source-selected state family contains diagnostic-associated bodies
for disconnecting, protocol selection, connecting, and connected idle. It
establishes numeric state writes, local transitions, and an MTP-selection
condition. Its effect-bearing calls remain virtual or otherwise opaque: no
accepted target resolves to the known MTP start/end bodies or wrappers, and no
source-owned host input selects the disconnect side. It therefore does not
establish a logical communication close/start or an unattended physical USB
cycle.

| Role | Local address | Block | Offset | Length |
|---|---:|---:|---|---:|
| Conditional disconnect producer | `0x6ecd03cc` | 0 | `0x006d03ec` | 63 |
| Disconnecting unmount-storage body | `0x6ecd0413` | 0 | `0x006d0433` | 108 |
| Disconnecting unmount-media body | `0x6ecd04c0` | 0 | `0x006d04e0` | 127 |
| Disconnecting end-communication body | `0x6ecd0580` | 0 | `0x006d05a0` | 108 |
| Disconnecting-done body | `0x6ecd062d` | 0 | `0x006d064d` | 170 |
| Disconnect body | `0x6ecd06e7` | 0 | `0x006d0707` | 36 |
| Connecting local producer | `0x6ecd070b` | 0 | `0x006d072b` | 85 |
| Connecting-start body | `0x6ecd09aa` | 0 | `0x006d09ca` | 147 |
| Protocol-selection body | `0x6ecd0b0b` | 0 | `0x006d0b2b` | 691 |
| Connecting mount-storage body | `0x6ecd0dff` | 0 | `0x006d0e1f` | 108 |
| Connecting mount-media body | `0x6ecd0eac` | 0 | `0x006d0ecc` | 151 |
| Connecting-error body | `0x6ecd0fc7` | 0 | `0x006d0fe7` | 201 |
| Connecting-done body | `0x6ecd10a0` | 0 | `0x006d10c0` | 173 |
| Connected-idle body | `0x6ecd16cc` | 0 | `0x006d16ec` | 130 |
| Dispatcher owner-candidate gate | `0x6eccfde9` | 0 | `0x006cfe09` | 88 |
| Parent-chain preservation callee | `0x6eccfec3` | 0 | `0x006cfee3` | 16 |

These anchors are selected from 35 canonical ranges under the conditional
CODE-local view `source + 0x6e5fffe0`; the accepted instruction set adds 60
contextually verified rows. Four additional canonical rows at source
`0x006cfbd8`, `0x006cfbed`, `0x006cfbf4`, and `0x006cfbf6` load receiver field
`+172`, scale the current value by four, load a table-selected pointer, and
jump through it. They do not establish the table entries or the state input's
owner. The wider proposed dispatcher range was not admitted because it stopped
before its return.

### State fields and diagnostic labels

The diagnostic names were checked as contextual source during semantic review:
their exact strings lie outside these canonical ranges, while unique pointer
operands occur in the selected bodies. The pointers label the bodies; they are
not written to the receiver. In particular, each body first writes a numeric
state to `+172` and to another state field, then loads its diagnostic pointer
separately for a reporting call. The disconnecting bodies write values 6
through 9 to both `+408` and `+172`; the disconnect body writes 10 to `+404`
and `+172`. The selected connecting bodies write 12 through 17 to `+412` and
`+172`, while connected idle writes 23 to `+416` and `+172`.

### Disconnect input and receiver boundaries

The producer at source `0x006d03ec` calls an empty-preservation-mask helper,
then tests a virtual slot `+8`. Its nonzero arm reaches a local helper and the
wrapper at source `0x006d06ff`, which directly calls the disconnect body at
`0x006d0707`. The empty-mask calls leave the receiver and result owner
unproved, so this is a local conditional edge rather than a host or USB input.

The dispatcher's separate owner-candidate arm passes its entry receiver `D`
to the complete body at source `0x006cfe09`. That body crosses two direct
empty-mask calls before its first virtual slot `+8` at source `0x006cfe26`;
the current helper result, table, and receiver are not source-bound to `D`.
Later calls therefore cannot establish a `D`-owned parent chain. This is the
first unresolved dynamic boundary, not evidence of a physical disconnect
producer.

### End-communication receiver and method

In the end-communication body, the current receiver `R` supplies
`P = *(R + 180)`. The body calls virtual slot `+36` from `P` with the adjacent
argument source `R + 264`, then later reaches separate allocation, helper, and
virtual-slot-`+28` machinery. The slot-`+36` target does not resolve to the
known MTP-end body at source `0x00258d2f`, its wrapper at `0x008181ba`, or
another explicit communication/interface close.

A nearby helper contributes 12 accepted rows across source
`0x006cf67d..0x006cf697` (CODE-local `0x6eccf65d..0x6eccf677`). With its entry
object named `X`, the rows compute `X + 180`, read and compare that field with
zero, and later load `*(X + 392)` and store it through the computed `X + 180`
address. The intervening branch row is not canonical, so these rows alone do
not establish the predicate controlling that store. The accepted tail reloads
`X + 180`, dereferences the loaded object, and calls its virtual slot `+80`.
Six isolated rows at sources `0x006cfdf4`, `0x006cff1f`, `0x006cff25`,
`0x006cff2b`, `0x006cff2e`, and `0x006cff34` retain nearby reload,
register-copy, return, and comparison anchors. The complete range-only body at
source `0x006cfee3` writes 4 to receiver field `+168`, calls one helper while
explicitly preserving `a2`, and returns without overwriting it. This repairs
the local `X` preservation through the following field helper, but the
upstream owner-candidate boundary still does not bind `X`, `R`, and dispatcher
receiver `D` as one object. Slot `+80` also remains distinct from the
unresolved end-communication slot `+36`.

### Connecting and protocol selection

On the connect side, source `0x006d072b` directly reaches the state-11 wrapper,
which calls the protocol-selection body. The connecting-start body invokes
unresolved slots `+96`, `+52`, and `+40` on objects obtained through receiver
field `+180`, with receiver-relative argument sources `+264`, `+312`, and
`+288`. It contains no direct call to the known MTP-start body at source
`0x00258ccb` or its wrapper at `0x008181d9`.

The protocol body reads `P = *(R + 184)`. A null value selects its protocol
error diagnostic; otherwise virtual slot `+76` must return nonzero before the
protocol comparison. Equality between `*P` and `*(R + 392)` selects the
MassStorage diagnostic. If that comparison fails, equality between `*P` and
`*(R + 388)` selects the MTP diagnostic; otherwise the PC Link diagnostic is
selected. The MTP-labelled arm converges on unresolved helper and virtual-call
machinery, not a source-resolved MTP re-entry target.

The later selected bodies retain the mount-storage, mount-media, error, done,
and connected-idle state writes. Connected idle invokes unresolved virtual
slots including `+168`, `+172`, `+200`, `+204`, `+56`, and `+44` on objects
derived from receiver fields. State names, numeric writes, and these calls do
not prove logical close/start, active USB teardown, host-visible detach or
enumeration, shooting availability, pending-action survival, capture, image
identity, host transfer, or patch safety.

**Next evidence:** source-bind the current result, table, and receiver at the
first owner-candidate slot `+8` boundary, or find an independent physical
disconnect producer. Then identify the end-communication slot `+36` and
connecting/MTP virtual targets. See
[communication receivers](../RESEARCH.md#r-usb-communication-receiver) and
[physical event ownership](../RESEARCH.md#r-usb-event-owner).

<a id="usb-disconnect-name-maps"></a>
### USB-labelled name maps and lookup boundaries

Three connected/disconnected name pairs occur in separate lookup domains, but
their accepted consumers are resource or formatting paths rather than a
physical USB-event owner. The rows authenticate names, numeric companions,
complete tables, and two lookup bodies; they do not select the PC/USB or
communication-state release dispatchers.

| Role | Local address | Block | Offset | Length |
|---|---:|---:|---:|---:|
| Complete `EV_*` lookup body | source only | 0 | `0x00596a2d` | 74 |
| `EV_USB_CONNECTED` string | DATA-local `0x6ee45605` | 0 | `0x008441e5` | 17 |
| `EV_USB_DISCONNECTED` string | DATA-local `0x6ee45616` | 0 | `0x008441f6` | 20 |
| Complete `EV_*` table | DATA-local `0x6ee45de4` | 0 | `0x008449c4` | 892 |
| Complete OLY 77/78 lookup body | source only | 0 | `0x009d7632` | 64 |
| `OLY_USB_CONNECTED` string | DATA-local `0x6f11d520` | 0 | `0x00b1c100` | 18 |
| `OLY_USB_DISCONNECTED` string | DATA-local `0x6f11d532` | 0 | `0x00b1c112` | 21 |
| Complete OLY 8/9 table | DATA-local `0x6f11d7c8` | 0 | `0x00b1c3a8` | 872 |
| Complete OLY 77/78 table | DATA-local `0x6f11f388` | 0 | `0x00b1df68` | 2,528 |

The conditional DATA-local view for these rows is `source + 0x6e601420`.
The `EV_*` pair has numeric companions 9 and 10. The two OLY tables reuse the
same name pointers but assign separate numeric domains: 8/9 and 77/78. Pointer
reuse does not make those domains aliases.

The OLY 77/78 lookup at source `0x009d7632` scans eight-byte records, compares
the numeric word, and obtains the pointer at record offset `+4`. It passes the
selected pointer as data to direct helpers rather than invoking it as a code
target. Its first unresolved receiver/meaning boundary is the call at source
`0x009d765d`; the body has no edge to either accepted release dispatcher. Its
only direct caller invokes another helper before forwarding the numeric key;
that helper clears the saved value and can produce only 0 or 1, not 8, 9, 77,
or 78. The `EV_*` body and separate OLY 8/9 scan likewise terminate in
resource/formatting helpers without a release-dispatch edge.

No accepted map row, table relation, direct call, or registrar establishes a
physical/interface producer for these names. The required pivot is a
source-authenticated producer with a preserved event object and value into the
PC/USB dispatcher at source `0x009d39ee` or the communication-state dispatcher
at source `0x006cfbd2`. The maps do not prove logical close, physical teardown,
host detach or re-enumeration, shooting availability, capture, image ownership,
or transfer.


**Next evidence:** [Physical event ownership](../RESEARCH.md#r-usb-event-owner).
