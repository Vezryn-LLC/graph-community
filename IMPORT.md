# Independent source history

The public `Vezryn-LLC/graph-community` repository already has independent history.
Normal contributions branch from that history; do not repeat the initial import
or replace its root. A normal clone of this public repository is appropriate.

Never merge, mirror-push or import the private producer's Git objects, ancestry,
refs, remotes, LFS metadata, submodules, worktree metadata or runtime state.
Deleting private files in a new commit does not remove reachable private history.
Read reviewed source files only, check rights/notices, adapt deliberately, and
commit them on the public repository's own branch. Keep private input identity,
operational evidence and account data outside the public payload.

The positive payload allowlist and manifest are reviewed together. Run
`python3 -B ci/check.py` before commit and on the final candidate. When Git metadata
is present, the checker verifies that all reachable refs retain only the original
public root, with no alternates, grafts or replacement refs. A history-free archive
can pass payload checks but cannot establish Git ancestry; the result states that
limit. Inspect the actual public diff and commit author/committer metadata too.

Future history-free exports, new destinations, visibility changes, tags and
releases require their own explicit authority and notice review. Neither this
procedure nor a manifest hash grants publication authority. Preserve the existing
v0.1.0 tag/artifacts; prepare compatible updates on a new branch.
