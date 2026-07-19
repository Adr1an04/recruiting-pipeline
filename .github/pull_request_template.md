## Summary

<!-- What problem does this solve, and why does it belong in Erga? -->

## Changes

-

## Product and security boundary

<!-- Note any untrusted input, network access, credentials, local writes, execution, or external actions. -->

- [ ] This change does not submit applications, send messages, mutate mail, or invent career evidence.
- [ ] New permissions or capability changes are documented and narrowly scoped.
- [ ] No personal data, credentials, local databases, or generated private artifacts are included.

## Verification

- [ ] `uv run ruff format --check .`
- [ ] `uv run ruff check .`
- [ ] `uv run mypy src`
- [ ] `uv run python -m unittest discover -s tests -v`
- [ ] `uv build`
- [ ] `git diff --check`

## Compatibility

<!-- Describe command, configuration, storage, MCP-tool, or credential migrations. Write "None" if not applicable. -->
