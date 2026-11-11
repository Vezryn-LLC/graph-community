# Zero-history import — procedure only

This procedure creates no repository or remote by itself. Publication requires
owner approval of the final destination/name, rights/license/notices, security
contact and supported launch scope. The current preflight does not authorize a
public repository, visibility change, release/tag, source transfer or paid CI.

1. Rebuild/check the reviewed candidate with the private builder into a new
   mode-0700 directory. Preserve its manifest hash and the private lineage report.
   Keep a pristine copy separate from all smoke/runtime work.
2. Copy only that exact verified payload to a new empty private directory outside
   every existing Git worktree. Do not use `git clone`, `git push --mirror`, a
   source-repo branch, `git archive` of the mixed repo, or copy `.git`. Do not copy
   caches, refs, remotes, LFS metadata, submodules, worktrees or runtime state.
3. Inspect every file, including hidden files, and compare against MANIFEST.json.
   `ci/check.py` verifies names/hashes and entrypoints before stateful use. Ensure
   `git rev-parse --show-toplevel` fails in the import directory before `git init`;
   a containing repository would silently reuse private metadata.
4. Only when specifically authorized for import, initialize new history locally:

   ```sh
   git -c init.templateDir= init --initial-branch=main
   git config --local user.name 'APPROVED PUBLIC AUTHOR'
   git config --local user.email 'APPROVED PUBLIC EMAIL'
   git add -- .
   git diff --cached --stat
   git -c core.hooksPath=/dev/null commit -m 'Initial reviewed Community source'
   git rev-list --all --count       # exactly 1
   git remote -v                   # empty
   git for-each-ref                # only the new intended branch
   git ls-tree -r --name-only HEAD # exact reviewed list
   ```

   Replace author placeholders with approved public identity. Inspect the actual
   commit object: author/committer name, email, timestamps and commit text are
   newly public metadata too. Check for Git alternates, grafts, replace refs,
   object directories, shared worktree metadata and environment-injected Git
   configuration; fresh history must have no source-repo object dependency.
5. The approved Apache-2.0 LICENSE is already in the private manifest.
   Incorporate verified security contact and approved release documentation,
   regenerate the manifest for those changes, then recheck the exact final tree
   and its independent Git history. A license does not itself authorize publication.
6. Only after separate remote/publication authorization, add the exact approved
   destination and push only `main`. Do not push all branches/tags or mirror.
   Independently verify remote visibility, default branch, file list and commit
   ancestry. Do not activate `ci/smoke.yml.example` until runner/billing authority
   is established. No remote commands or release commands are executed here.

A normal push from the original mixed repository would transmit every ancestor
reachable from the pushed branch, including private source, metadata and deleted
files. Deleting files in a new commit or renaming a branch does not remove that
history. Some other refs travel only if pushed, but reachable ancestors already
make an ordinary source-branch push unsafe. Use only the new independent history.
