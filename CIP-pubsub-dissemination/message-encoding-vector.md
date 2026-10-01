# Message encoding test vector

This vector checks the byte construction specified under [Messages](README.md#messages), using the [shared encoding rules](README.md#canonical-encoding-and-domain-separation). The field values are synthetic; this is an encoding example, not a publication from a registered topic or a test of message authorisation.

Byte strings below are hexadecimal. The signature input uses the decoded bytes, not the hexadecimal text. Integer field values are decimal.

| Field | Value |
| --- | --- |
| Domain tag (UTF-8) | `pubsub/message/v1` |
| `topic` | `000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f` |
| `publisher` | `d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a` |
| `parent` | `202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f` |
| `sequence` | `42` |
| `timestamp` | `1700000000123` |
| `payload` | `68656c6c6f` (`hello` in UTF-8) |

The signature input is the concatenation of the following seven lines, in order: `LP(domain tag)`, `LP(topic)`, `LP(publisher)`, `parent`, `sequence`, `timestamp`, `LP(payload)`. Line breaks are for display only. Each length prefix is four bytes; the two integers are eight bytes each. All integers are unsigned and big-endian.

```text
000000117075627375622f6d6573736167652f7631
00000020000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
00000020d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a
202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f
000000000000002a
0000018bcfe5687b
0000000568656c6c6f
```

Total signature-input length: **150 bytes**.

The message hash is SHA-256 of those bytes:

```text
4f2a4f658e6a08030a0cdaa5232e581d7948383257c7ab049e4e6932ac35906c
```

Neither the signature nor any framing used to transmit the message is included in this input.
