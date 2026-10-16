# CatalystEdge submission checklist

## Code release

- [ ] Tests, Ruff, and compileall pass in the project venv.
- [ ] MCP registry exposes exactly the documented tools.
- [ ] Wheel and source distribution include `data/events.json`.
- [ ] Deterministic demo runs without a key or network.
- [ ] README commands match actual output.
- [ ] Repository contains LICENSE and no secrets.
- [ ] Fresh-clone verification passes.
- [ ] Public tag and commit are recorded here.

## Event integrity

- [ ] Recheck FOMC meeting and release times against the Federal Reserve.
- [ ] Recheck November 3 election date against USA.gov.
- [ ] Preserve the analytical-window disclaimer for election results.
- [ ] Do not claim the bundled catalog is complete.
- [ ] Custom events remain labeled unverified.

## Marketplace package

- [ ] ZIP has exactly one top-level `catalystedge/` directory.
- [ ] ZIP contains only `SKILL.md` and `LICENSE`.
- [ ] Folder and frontmatter names exactly match.
- [ ] Files are regular UTF-8 text with mode 0644.
- [ ] No symlinks, traversal paths, credentials, executables, or hidden files.
- [ ] SHA-256 is recorded.
- [ ] Security declaration matches the final release.

## Human/account steps

- [ ] Owner reviews final listing and artifact hash.
- [ ] Owner completes Agensi login, identity, and Stripe Connect requirements.
- [ ] Upload only the audited ZIP.
- [ ] Verify the published listing and download after approval.
