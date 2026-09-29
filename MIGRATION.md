# Migration Guide: extracting Alberto Research from the private monorepo

This document describes how to move `alberto-research` out of the private
`Alberto` monorepo and into a clean, standalone public repository **without
carrying over monorepo history, unrelated packages, secrets, or operational
data**.

The guiding rule is: **export the current tree, not the history.** A fresh
repository with a single signed initial commit is easier to audit, review and
trust than a filtered history that may still contain removed secrets. If you
ever need to prove provenance, the private monorepo remains the historical
record.

> **Do not run the push commands in this document without explicit
> confirmation from the author.** Publishing is irreversible in practice — once
> a secret or a private path is public, rewriting history does not unpublish it.
> See [Publishing](#step-9--publishing-requires-explicit-author-confirmation).

## Preconditions

- A working copy of the private `Alberto` monorepo, with a clean working tree.
- `git` 2.30 or newer, with commit and tag signing configured
  (`user.name`, `user.email`, `user.signingkey`, and `commit.gpgsign` or
  `tag.gpgsign` as preferred). No email address belongs in this document; use
  whatever identity is already configured in your environment.
- The secret scanners used below, installed and on `PATH`:
  `gitleaks`, `trufflehog`, and `detect-secrets`.
- `uv` and Python 3.11 for the post-migration smoke test.

Let us set some paths once. Adjust them to your machine:

```bash
MONOREPO=/path/to/Alberto
PACKAGE_PATH=src/alberto/research
EXPORT=/path/to/export/alberto-research
WORKTREE=/path/to/worktrees/alberto-export
```

## Step 1 — Create a dedicated worktree of the monorepo

Use a worktree rather than your everyday checkout, so the export cannot disturb
in-progress work and so you can delete the whole thing afterwards.

```bash
cd "$MONOREPO"
git fetch --all --prune
git worktree add --detach "$WORKTREE" origin/main
cd "$WORKTREE"
git status --short   # must be empty
```

Record the source revision for the migration notes:

```bash
git rev-parse HEAD | tee "$WORKTREE/.migration-source-revision"
```

## Step 2 — Export the package tree into a clean directory

Copy only the package subtree, then remove anything that is not part of the
published artifact. Copy the content of the package directory, not the parent
directory itself.

```bash
mkdir -p "$EXPORT"
rsync -a --delete "$WORKTREE/$PACKAGE_PATH/" "$EXPORT/"
```

Remove caches, environments, local databases, and build output that may have
leaked into the tree:

```bash
cd "$EXPORT"
rm -rf .venv .mypy_cache .pytest_cache .ruff_cache .hypothesis \
       build dist .eggs .tox htmlcov coverage.xml .coverage
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.py[cod]' -type f -delete
find . -name '.DS_Store' -type f -delete
```

Keep the files you intend to publish, and confirm the expected set is present:

```bash
ls -la "$EXPORT"
```

If the export is incomplete, fix the copy in Step 2 rather than committing a
partial tree.

## Step 3 — Initialise the clean public repository

Create a brand-new repository with `main` as the initial branch. Do **not**
clone the monorepo and do **not** copy its `.git` directory.

```bash
cd "$EXPORT"
git init -b main
git config user.name "$(git -C "$WORKTREE" config user.name)"
git config user.email "$(git -C "$WORKTREE" config user.email)"
```

If you have a signing key configured globally, verify it before committing:

```bash
git config --get user.signingkey
git config --get commit.gpgsign
```

Optionally add a public remote now but do not push:

```bash
git remote add origin https://github.com/gabriel-affonso/alberto-research.git
git remote -v
```

At this point nothing is staged and nothing is committed. Scanning an untracked
tree is exactly what the next step is for.

## Step 4 — Scan for secrets before the first commit

Run all three scanners. They look for different things and miss different
things; a clean result from one is not a substitute for the others. Use
`--no-git` for `gitleaks` so it scans the working tree rather than a history
that does not exist yet.

```bash
# 1. gitleaks: pattern- and entropy-based secret detection over the tree.
gitleaks detect --source . --no-git --redact --verbose

# 2. trufflehog: verified-credential detection. --only-verified keeps the
#    output focused on credentials that were actually confirmed live.
trufflehog filesystem . --only-verified

# 3. detect-secrets: baseline scan with its full plugin set.
detect-secrets scan --all-files --exclude-files '\.secrets\.baseline$' \
  > .secrets.baseline
detect-secrets audit .secrets.baseline
```

Evaluate the output:

- **Any hit is a blocker.** Do not proceed, do not "fix it later", and do not
  assume a hit is a false positive without confirming it.
- Rotate any credential that appears, even if it looks expired or fake. Removal
  from the tree does not un-leak a value that was ever written to disk or pushed.
- `.secrets.baseline` records known, reviewed findings without storing the
  secrets themselves. Commit it only if you have actually audited every entry;
  otherwise delete it and let the scanner run clean.

Then scan the manifest and source paths manually for anything the tools do not
catch:

```bash
# Local paths, private hostnames, internal URLs, personal data.
grep -RInE '(/Users/|/home/|\.local/|internal\.|corp\.|vpn\.)' . \
  --exclude-dir=.git || true

# Environment files and key material that should never be published.
find . -path ./.git -prune -o \
  \( -name '*.env' -o -name '.env*' -o -name '*.pem' -o -name '*.key' \
     -o -name '*.p12' -o -name '*.sqlite' -o -name '*.db' \) -print
```

## Step 5 — Review the export by hand

Before committing, confirm:

- [ ] `LICENSE` is present and is the intended MIT licence.
- [ ] `README.md` describes the public project and contains no internal context.
- [ ] `pyproject.toml` has no private index URLs, no path dependencies, and no
      monorepo-relative references.
- [ ] No operational data: databases, downloaded PDFs, digest archives, run
      logs, or exported Zotero/Notion content.
- [ ] No credentials, tokens, cookies, session files, or OpenClaw configuration
      containing secrets.
- [ ] No personal data belonging to anyone else.
- [ ] Governance files are present: `SECURITY.md`, `CONTRIBUTING.md`,
      `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`, `ROADMAP.md`, `CHANGELOG.md`,
      `CITATION.cff`, `ACKNOWLEDGMENTS.md`, `.all-contributorsrc`.
- [ ] The shadow-library resolvers are still disabled by default and the legal
      notice in `SECURITY.md` still matches the code.
- [ ] `git status --short` shows only files you intend to publish.

## Step 6 — Stage and create the signed initial commit

```bash
cd "$EXPORT"
git add -A
git status --short

# Review what is about to be committed before committing it.
git diff --cached --stat
git diff --cached --name-only
```

Only when the staged set is correct, create a **signed** initial commit (`-S`):

```bash
git commit -S -m "chore: initial public release of alberto-research

Extracted from the private Alberto monorepo as a standalone package.
Source revision: $(git -C "$WORKTREE" rev-parse HEAD)" \
  -m "Signed-off-by: $(git config user.name) <$(git config user.email)>"
```

Verify the signature before tagging anything:

```bash
git log --show-signature -1
git verify-commit HEAD
```

## Step 7 — Tag the release with a signed tag

```bash
git tag -s v0.1.0 -m "alberto-research v0.1.0"
git tag -v v0.1.0
git show --stat v0.1.0
```

Update the source-revision note if you want it tracked in-tree, then amend only
if the tree itself changed; otherwise leave the commit alone. Never move a
published tag — cut a new one instead.

## Step 8 — Verify the exported tree before publishing

Run the package's own gates against the clean checkout, so a missing file in the
export cannot surprise anyone after publication:

```bash
uv venv --python 3.11
uv pip install -e ".[dev]"
pre-commit run --all-files
pytest
```

Also confirm the build works from the clean tree:

```bash
uv build
ls -la dist/
```

## Step 9 — Publishing (requires explicit author confirmation)

> **STOP.** The commands in this section are intentionally commented out.
> Pushing publishes the repository and its history to the world. Do not enable
> them until the author has explicitly confirmed, in writing, that the export is
> approved — after Step 4's scans came back clean, Step 5's checklist was
> completed, and Step 8 passed.

```bash
# ---------------------------------------------------------------------------
# PUSH SECTION — DISABLED. Requires explicit confirmation from the author.
# Do not uncomment, and do not run these commands, without that confirmation.
# ---------------------------------------------------------------------------
#
# # Push the initial commit and the release tag to the public repository.
# git push -u origin main
# git push origin v0.1.0
#
# # Verify what actually landed on the remote.
# git ls-remote --heads origin
# git ls-remote --tags origin
# ---------------------------------------------------------------------------
```

If a push is approved, prefer a final `git push --dry-run` first, and confirm
the remote URL points at the intended public repository and not at the private
monorepo.

## Step 10 — Post-migration tasks

Once the public repository is live and the release is published:

1. **Configure the public repository.** Enable branch protection on `main`
   (require pull requests, require the quality-gate checks, require signed
   commits or DCO). Enable **private vulnerability reporting** so
   [SECURITY.md](SECURITY.md) works. Add the all-contributors bot and any
   release automation.
2. **Publish the package.** Configure the release workflow or trusted publisher
   for the package index, and release `v0.1.0` from the signed tag.
3. **Archive the old repository — do not delete it.** The private monorepo and
   the in-tree copy are the historical record and may still be referenced by
   open pull requests or notes. Archive it so it becomes read-only:
   - GitHub: **Settings → General → Danger Zone → Archive this repository**, and
     update the description to point at the new public repository.
   - Add a short note to the top of its README, for example
     `> Archived. Development has moved to
     > https://github.com/gabriel-affonso/alberto-research`.
   - If the monorepo is not on GitHub, make the mirror read-only and record the
     new canonical location wherever the old one was documented.
4. **Remove the in-tree copy in the monorepo.** In a follow-up pull request on
   the archived source, delete the package directory and point any remaining
   imports at the published package. Do this *after* archiving, so the archive
   still contains a complete, self-consistent tree.
5. **Clean up the migration workspace.** Remove the temporary worktree and
   export once the archive is confirmed:

   ```bash
   git -C "$MONOREPO" worktree remove "$WORKTREE"
   git -C "$MONOREPO" worktree prune
   ```

6. **Record the migration.** Note the source revision, the date, and the people
   involved in the new repository (for example in the initial commit message or
   a short `docs/migration.md`).

## Rollback

- **Before pushing:** delete the export directory and start over. Nothing
  irreversible has happened. The monorepo worktree is disposable:

  ```bash
  git -C "$MONOREPO" worktree remove --force "$WORKTREE"
  ```

- **After pushing, before anyone has cloned:** you can force-push a corrected
  history, but treat this as an emergency and coordinate with the author first.
- **After publication:** do not rewrite history. Rotate anything exposed, cut a
  new patch release, and document the incident.

## Verification checklist

- [ ] Scanners run and clean: `gitleaks detect --source . --no-git`,
      `trufflehog filesystem . --only-verified`, `detect-secrets scan`.
- [ ] Initial commit is signed (`git verify-commit HEAD`).
- [ ] `v0.1.0` tag is signed (`git tag -v v0.1.0`).
- [ ] Quality gates pass on the clean checkout.
- [ ] Push explicitly authorised by the author before running any push command.
- [ ] Public repository configured: branch protection, private vulnerability
      reporting, the all-contributors bot.
- [ ] Old repository archived, not deleted, with a pointer to the new location.
- [ ] Temporary worktree and export directory removed.
