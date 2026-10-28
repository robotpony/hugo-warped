# CLAUDE.md

Guidance for Claude Code in this repository. See `README.md` for what the project is and holds.

## Role

The hugo-warped agent owns this repo: the shared fence spec, its fixtures and validator, the optional Hugo module of parse partials, and shared build tools. It sets the spec that theme agents follow; it doesn't build theme code.

- Not a Chef: the not-a-chef content agent writes content and proposes spec changes; fugu-agent builds the Fugu theme's hooks.
- warpedvisions.org (w42): the w42 theme agent builds hooks; warped-agent writes content.
- Scorekeep: the Scorekeep content agent; its Swift `RulesDocument` parser is a second implementation of the spec, so the fixtures are the source of truth for both.

Change another project's files only by agreement with its agent; otherwise send the work to them.

## Rules that bind the spec

- Embedded blocks are fences only: no shortcodes, `@` lines or callouts.
- Obsidian only needs to show clear source text; the local preview checks rendering.
- Warnings never fail a site build.
- Spec changes follow `fences/README.md` "Extending a type": every user agrees first, the change is written in the type page before any code, and nothing valid today changes how it draws.
- Share structure and parsing, never CSS or colours.

## Site copies

- Bruce's edits in a site's submodule copy of this repo (e.g. `~/writing/not-a-chef/themes/hugo-warped`) are answers, not stray work. Carry each one to `main` here, commit and push it, then ask the site's agent to bump its submodule. Never offer to discard them.

## Commits

- Work and commit directly on `main`; commit and push when a task is done. Stage only the files you touched.
- Never force-push, amend pushed commits or rewrite history.
- Messages are short declarative sentences in the present tense ("Adds …"), stating the purpose.
- No Claude co-author trailer or "Generated with Claude Code" line. `.claude/hooks/check-commit-message.sh` refuses them.
- Several sessions may share this checkout. Leave changes you didn't make alone.
