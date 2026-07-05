---
status: accepted
---

# DynamoDB as the primary Paste datastore

Pastes need durable storage with a single access pattern: write once, then read by ID. PostgreSQL was considered as the alternative — it offers flexible ad-hoc querying (useful if features like "list recent pastes" or search are added later) and a more familiar local dev loop, but requires provisioning and operating an instance/cluster even in its "serverless" form, and buys nothing for an access pattern that never joins or filters.

DynamoDB matches the access pattern directly: single-digit-ms point reads by ID at any scale, fully serverless with no instance to manage, multi-AZ durability by default, and a built-in TTL attribute that's a free option if expiring pastes are added later. Its main constraint is the 400KB item size limit, since paste content lives directly in the item — if a paste exceeds this, the body would need to move to S3 with only metadata kept in DynamoDB.

The remaining objection to DynamoDB — a harder local dev/test loop than Postgres — is addressed by a two-tier testing strategy: `moto` mocks DynamoDB in-process for fast unit tests, and the official `amazon/dynamodb-local` Docker image (a real implementation of the DynamoDB engine, not a mock) runs in Compose for integration tests and local development, addressed by service name on the Compose network so CI and laptop runs are identical and fully offline. The app's DynamoDB endpoint is configurable via an environment variable so the same code path targets DynamoDB Local in dev/test and real DynamoDB in production.

Decision: DynamoDB is the primary datastore for Pastes.
