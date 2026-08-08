# Synthetic-data and privacy policy

GraphMedic's public entry must be reproducible without private, workplace, household, or personal data.

## Allowed

- Fictional dataset names under the `graphmedic_demo` platform.
- Invented stewardship identities such as `synthetic-steward`.
- Generated lineage, descriptions, scores, tests, and screenshots derived from that fictional catalog.
- Public organizer documentation and public open-source dependencies.

## Prohibited

- Employer names, systems, repositories, tickets, customer or coworker information.
- Personal email addresses, home or workplace addresses, private network addresses, machine names, credentials, tokens, or local absolute paths.
- Screenshots containing unrelated browser tabs, notifications, terminals, bookmarks, accounts, or desktop content.
- Claims based on tests or measurements that were not actually performed.

## Enforcement

Runtime reads and writes require all three opt-in markers: demo namespace, demo tag, and synthetic classification. Public artifacts pass a generic scanner plus a user-specific local scanner that is deliberately stored outside the repository. Screenshots and video are captured from isolated app windows showing only seeded fictional content.
