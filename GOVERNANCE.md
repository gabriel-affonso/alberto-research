# Governance

This document explains who decides what in Alberto Research, how decisions are
made today, and how the project intends to grow beyond its founding maintainer.

## Current model: BDFL

Alberto Research is currently a **Benevolent Dictator For Life (BDFL)** project.

- **Maintainer / BDFL:** Gabriel Affonso
  ([@gabriel-affonso](https://github.com/gabriel-affonso))
- The BDFL has final authority over technical direction, releases, and
  community matters, and is the only person with merge and release rights today.
- The BDFL is expected to act in the open, explain reasoning, and follow the
  same review and quality gates as everyone else. Authority is a tie-breaker and
  a safety valve, not a licence to bypass process.

This model is a starting point, not an end state. The project deliberately
documents a path away from it.

## Decision process

We prefer to decide by **lazy consensus** and to write down anything
non-obvious.

### Lazy consensus

- Proposals start as a GitHub issue (or a pull request with a written
  description) that states the problem, the options considered, and a
  recommendation.
- If nobody raises a substantive objection within **7 days**, the proposal is
  considered accepted and may be implemented.
- An objection must include reasoning. "I do not like it" is not a blocking
  objection; "this breaks X because Y" is.
- Silence is assent, but only for reversible decisions. Irreversible or
  disruptive changes require explicit approval from the maintainer.

### ADRs for non-obvious decisions

Architecture Decision Records (ADRs) are required for decisions that are hard to
reverse, affect public interfaces, or would surprise a future contributor.
Examples: the resolver plugin API, the storage schema strategy, the schema
validation boundary, and the trust model for LLM output.

- ADRs live in `docs/adr/` as `NNNN-short-title.md`, numbered sequentially.
- Each ADR records context, the decision, alternatives considered, and
  consequences, and its status (`proposed`, `accepted`, `superseded`,
  `deprecated`).
- Accepted ADRs are immutable in substance; to change a decision, add a new ADR
  that supersedes the old one.

### Escalation

If consensus cannot be reached, the BDFL decides and publishes the reasoning in
the relevant issue or ADR. Any participant may ask for a written rationale, and
the maintainer is expected to provide one.

## Release authority

- The BDFL is the release manager and holds the signing keys for release tags.
- Releases are cut from `main` only, only when `main` is green.
- Releases follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html),
  with the changelog maintained in [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
  format in [CHANGELOG.md](CHANGELOG.md).
- Release tags are annotated and signed (`git tag -s`). Artifacts are built from
  a clean checkout of the tagged commit.
- The release process is documented and repeatable; a future maintainer must be
  able to run it without the BDFL present.
- Delegation is allowed and encouraged: the BDFL may name a release manager for
  a specific release, with the scope and duration stated publicly.

## Path to meritocracy

The project intends to move from BDFL rule to a meritocratic, multi-maintainer
model. The transition is triggered by sustained contribution, not by
self-nomination alone.

### Stage 1 — Reviewers (2+ sustained contributors)

- **Trigger:** at least **two** contributors other than the BDFL have each made
  sustained, high-quality contributions over a period of roughly **three months
  or more** — for example several merged pull requests across more than one area
  (code, tests, docs), plus substantive participation in review or issue
  triage.
- **Appointment:** the BDFL invites the contributor, or the contributor asks and
  the BDFL confirms. The appointment is announced in a public issue.
- **Powers:** reviewers may approve pull requests in the areas they know, and
  their approval counts toward merge readiness. Reviewers do not merge or
  release unless the BDFL explicitly delegates that for a specific change.
- **Expectations:** reviewers keep responding to the areas they own, follow the
  quality gates, and recuse themselves from decisions where they have a conflict
  of interest.

### Stage 2 — Steering group

- **Trigger:** the project has **three or more** active maintainers (reviewers
  with merge rights), or sustained contribution regularly exceeds what one
  person can review.
- **Composition:** a small steering group of the active maintainers, with a
  designated release manager rotating or elected among them.
- **Decision rule:** lazy consensus first; if the group is split, a simple
  majority of steering-group members decides, and the BDFL retains a
  tie-breaking vote during the transition period.
- **Transition:** when the steering group is operating, this document is amended
  to describe its composition, term, and decision rules, and the BDFL role is
  reduced to that of an ordinary steering-group member. The change is announced
  publicly before it takes effect.

### How to become a maintainer

There is no application form. The route is:

1. **Contribute consistently.** Land reviewed changes across more than one part
   of the project.
2. **Review others.** Give careful, kind, specific feedback on other people's
   pull requests.
3. **Triage.** Help reproduce bugs, answer questions, and improve documentation.
4. **Be trusted with judgement.** Show that you weigh trade-offs, respect the
   threat model, and communicate clearly.
5. **Accept the invitation.** The BDFL (or, later, the steering group) invites
   you, states the scope of your rights, and records the appointment publicly.

Maintainer status is earned by sustained behaviour, and it can be revoked for
sustained inactivity or for violating the Code of Conduct; the expectation and
the process are documented in the next section.

### Stepping down and inactivity

- Maintainers may step down at any time; we will thank them and record it.
- A maintainer inactive for **six months** without notice moves to emeritus
  status. Emeritus maintainers keep credit and may return by asking.

## Conflict resolution

1. **Talk first.** Raise the disagreement directly and privately with the person
   involved, or in the pull request or issue where it arose. Assume good faith.
2. **Bring in a third party.** If direct discussion stalls, ask another
   contributor or reviewer to help find a middle ground.
3. **Escalate to the maintainer.** If the disagreement is still unresolved, the
   BDFL decides and publishes the reasoning. Once the steering group exists, it
   decides by the rule above instead.
4. **Code of Conduct matters are separate.** Harassment, personal attacks, and
   other conduct issues are handled under [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md),
   not through this technical escalation path.
5. **Appeals.** A decision may be appealed once, with new information or a
   concrete alternative. Re-litigating the same decision without new information
   is not productive and may be closed.

## Amending this document

Changes to this document are themselves governed by it: propose the change in a
pull request, allow 7 days for objections, and record the reasoning. The
committed file is the source of truth — this is a living document, and we would
rather update it than pretend it still describes reality.
