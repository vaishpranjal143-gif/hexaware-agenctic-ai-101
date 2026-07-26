#!/usr/bin/env bash
# Stage everything, commit with a rule-based number, and push to every remote.
# No AI involved — the commit message is derived purely from the commit count.
set -e

# Move to the repo root regardless of where the script is called from.
cd "$(dirname "$0")"

# Stage all changes (new, modified, deleted).
git add -A

# Rule-based commit number = existing commit count + 1.
NUMBER=$(( $(git rev-list --count HEAD 2>/dev/null || echo 0) + 1 ))
MESSAGE="commit $NUMBER"

# Commit only if there is something staged.
if git diff --cached --quiet; then
    echo "Nothing to commit."
else
    git commit -m "$MESSAGE"
    echo "Committed: $MESSAGE"
fi

# Push the current branch to every configured remote.
BRANCH=$(git rev-parse --abbrev-ref HEAD)
for REMOTE in $(git remote); do
    echo "Pushing to $REMOTE..."
    git push "$REMOTE" "$BRANCH"
done

echo "Done."
