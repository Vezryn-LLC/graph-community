# First issue: an uppercase greeting

This tiny exercise takes a few minutes to understand; agent execution time is not
promised. Python 3.11+ is enough to inspect and test it. It uses no account, model,
telemetry, enrollment or service. The outputs below are **expected fixture results**,
not a transcript of a Graph delivery.

## 1. Make a disposable local copy

From the Graph Community source root, create a fresh copy outside that source:

```sh
python3 -c "from pathlib import Path; import shutil,tempfile; target=Path(tempfile.mkdtemp(prefix='graph-first-issue-'))/'fixture'; shutil.copytree('examples/first-issue',target); print(target)"
```

Change into the printed directory. On Windows, use `python` where this page says
`python3`. Keep any real trial in a disposable repository you control, with no
production data, secrets or active assignment. The local copy does not enroll
anything or create a remote repository.

## 2. See the baseline and the missing behavior

```sh
python3 -B greet.py Ada
python3 -B -m unittest -v test_greet.GreetingTests.test_default
python3 -B -m unittest -v test_greet.GreetingTests.test_uppercase
```

Expected: `Hello, Ada!`, then one passing baseline test. The uppercase acceptance
test **fails** because `--uppercase` is deliberately missing. This red test is the
exercise, not a failed Graph installation. [ISSUE.md](ISSUE.md) is the exact bounded
request. You can implement it yourself locally; completion of the code exercise is:

```sh
python3 -B -m unittest -v test_greet
```

Expected after the change: both tests pass, default output stays `Hello, Ada!`,
and `python3 -B greet.py Ada --uppercase` prints `HELLO, ADA!`.

## 3. Optionally try the real issue-to-PR journey

Local testing above is sufficient to learn the task. To try Graph, first qualify
your own native tools, permissions and disposable **private** test repository using
the [Quickstart's canonical trial instructions](https://github.com/Vezryn-LLC/graph-community/blob/main/QUICKSTART.md#one-real-issue-only-after-native-hostaccount-authorization).
Start from the unchanged fixture, commit it to that repository, then use
[ISSUE.md](ISSUE.md) as one issue's title/body. Check existing claims, issues and PRs
before an authorized maintainer marks it `status:ready`. Enroll only that test
repository in an isolated trial profile; inspect `repo list` before any dispatch.
Never enroll a production repository for this exercise.

`ci/check.py` is Graph's accounts-free package validation. `queue` reads current
GitHub candidate metadata using your authenticated CLI. **`watch --once` is live
dispatch**, capable of launching a real coordinator and worker; it is not a dry-run
or a command needed by this fixture. Native Codex permissions still govern actions.
The [Wiki First Workflow](https://github.com/Vezryn-LLC/graph-community/wiki/First-Workflow)
explains the claim, isolated source, ordinary PR, validation and stop/drain stages;
the Quickstart owns the platform-specific commands.

## 4. Judge the actual result

For a real trial, inspect the actual remote PR diff, both test results and original
issue outcome. A merged PR with both tests passing can deliver this source-only
task; a local pass, process exit or PR URL alone does not prove Graph delivery.
No live Graph run or externally verified PR is claimed by this example.

If blocked or unverified, retain the same issue, claim, source and useful evidence.
Read the concrete blocker and check for a surviving worker or existing PR before
retrying; do not recreate the issue, launch a second watcher or delete state/source
to force a clean start. Resolve the stated gate, then follow
[recovery guidance](https://github.com/Vezryn-LLC/graph-community/wiki/Troubleshooting-and-Recovery).
