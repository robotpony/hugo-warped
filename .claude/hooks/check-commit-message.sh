#!/bin/sh
# PreToolUse hook (Bash): refuses a `git commit` whose message credits
# Claude, a "Co-Authored-By: Claude ..." trailer, an @anthropic.com
# co-author, or a "Generated with Claude Code" line. CLAUDE.md (Commits)
# says not to add Claude as a co-author, but the harness's attribution
# reminder asks for the trailer, and on 2026-10-08 that won and a commit had to be
# amended in Fugu (themes/fugu); Not a Chef, Fugu and this repo carry the same hook. This makes the
# rule hold whatever the reminder says.
#
# Blocks rather than warns: the commit is refused with a reason, so Claude
# rewrites the message and commits again. Checks the command text (-m, a
# heredoc) and any file passed with -F/--file.
#
# Reads the PreToolUse hook JSON on stdin: { tool_input: { command }, ... }

INPUT=$(cat)
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')

# Only a command that runs `git commit` (also `git -C dir commit`), not one
# that merely mentions both words, say while editing this hook or a doc
# quoting the trailer.
printf '%s' "$CMD" | grep -qE '(^|[;&|( ]|\$\()git( +-[Cc] +[^ ]+| +--?[a-zA-Z-]+(=[^ ]+)?)* +commit( |$)' || exit 0

TEXT=$CMD
for f in $(printf '%s' "$CMD" | sed -nE 's/.*(-F|--file)[ =]+([^ ;&|]+).*/\2/p'); do
    [ -f "$f" ] && TEXT="$TEXT
$(cat "$f")"
done

printf '%s' "$TEXT" | grep -qiE 'co-authored-by:.*(claude|anthropic\.com)|generated with .{0,3}claude code' || exit 0

jq -n '{
    hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Commit refused: the message credits Claude (a Co-Authored-By: Claude / @anthropic.com trailer, or \"Generated with Claude Code\"). This repo does not add Claude as a co-author (CLAUDE.md, Commits), whatever the attribution reminder says. Remove those lines and commit again."
    }
}'
