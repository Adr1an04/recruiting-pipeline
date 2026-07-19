# Versioning and releases

Erga follows semantic-versioning conventions with `v`-prefixed Git tags.

## Before 1.0

The public interfaces are still evolving:

- `0.MINOR.0` may introduce features and intentional breaking changes;
- `0.MINOR.PATCH` contains compatible fixes and documentation improvements; and
- migration notes accompany changes to commands, configuration, storage, MCP tools, or credential
  identifiers.

Pre-alpha releases support only the latest published minor line.

## Release checklist

1. Update the version in `pyproject.toml` and `uv.lock`.
2. Update `CHANGELOG.md` with user-visible changes and migrations.
3. Run the complete verification suite from `CONTRIBUTING.md`.
4. Commit the release, create an annotated `vX.Y.Z` tag, and push the tag.
5. Verify the GitHub Actions release build and attached wheel/source archive.

The release workflow builds artifacts on version tags. Publishing to a package index is a separate,
explicit maintainer action.
