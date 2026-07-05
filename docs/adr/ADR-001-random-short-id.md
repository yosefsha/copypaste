---
status: accepted
---

# Random short URL IDs, not content-derived hashes

A Paste needs a short URL identifier. Two approaches were considered: a random ID generated at write time, or an ID derived from a hash of the paste's content (content-addressing, as in git).

Content-addressing was attractive for free deduplication — identical text always resolves to the same URL, so storage is never duplicated. It was rejected for two reasons. First, it leaks information: anyone who already has (or guesses) the same content can independently derive its URL, which is an unexpected form of exposure for a pastebin where users may assume their URL is only discoverable by those they share it with. Second, and decisively, Pastes are planned to support a mutable version later. A content hash is only stable as long as content doesn't change — it cannot serve as a stable identifier for an object whose content is expected to be edited in place, since editing the content would change the hash and break the URL.

Decision: short URL IDs are randomly generated at write time, independent of content. Identity and content are decoupled, which is a prerequisite for adding mutation later without changing how Pastes are addressed.
