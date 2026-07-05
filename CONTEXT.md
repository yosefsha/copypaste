# copypaste

A pastebin-style service: users submit text and receive a short URL that retrieves the same text later, from any device.

## Language

**Paste**:
An immutable text object submitted by a user, identified by a short URL. Once created, its content never changes — resubmitting different text produces a new Paste with a new short URL, not an update to the old one.
_Avoid_: Snippet, entry

