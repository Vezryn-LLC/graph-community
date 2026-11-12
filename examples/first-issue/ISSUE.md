# Add an optional uppercase greeting

`greet.py` prints `Hello, Ada!` for `python3 -B greet.py Ada`, but rejects
`--uppercase`. Add that optional flag so `python3 -B greet.py Ada --uppercase`
prints exactly `HELLO, ADA!` followed by a newline and exits successfully.
Keep the default greeting unchanged. Use only the Python standard library;
make no network calls and add no services, credentials or dependencies.

Acceptance: from this fixture's directory, `python3 -B -m unittest -v test_greet`
passes both tests. The PR should contain the small CLI change and its validation
evidence. A blocked run or an unmerged PR is not completed delivery.
