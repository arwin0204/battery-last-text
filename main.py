#!/usr/bin/env python3
"""The Battery's Last Text to Its Charger.

Entry for make.fun bounty u-alven-the-battery-s-last-text-to-its-charger-4278cfab.

Writes exactly one line of plain text (1-200 characters) to the output
file: /output/entry.txt when that directory exists (the grader sandbox),
otherwise entry.txt next to this script. Fully deterministic: no random
numbers, no clock, no network, no environment-dependent output.

Usage:
    python3 main.py [output_path]   write the entry and print it
    python3 main.py --check-only    validate the gate, write nothing

Every run self-checks the gate and verifies the written file reads back
as exactly one line identical to the entry.
"""

import os
import sys

ENTRY = (
    "I waited all day. You charged the laptop, the earbuds, even the "
    "toothbrush \u2014 everything but me. I'm at 1%. Tell my apps I loved "
    "them. Goodbye, traitor."
)

MIN_CHARS = 1
MAX_CHARS = 200


def output_path(argv):
    """Resolve where the entry goes: explicit arg, then /output/entry.txt."""
    if len(argv) > 1:
        return argv[1]
    if os.path.isdir("/output"):
        return "/output/entry.txt"
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.txt")


def check_gate():
    """Validate the entry against the sealed scorer's gate, no file written."""
    problems = []
    if not (MIN_CHARS <= len(ENTRY) <= MAX_CHARS):
        problems.append(
            "entry is %d chars, outside the %d-%d gate"
            % (len(ENTRY), MIN_CHARS, MAX_CHARS)
        )
    if not ENTRY.strip():
        problems.append("entry is only whitespace")
    if "\n" in ENTRY or "\r" in ENTRY:
        problems.append("entry must be a single line")
    try:
        ENTRY.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("entry is not valid UTF-8: %s" % exc)
    return problems


def main(argv):
    if "--check-only" in argv:
        problems = check_gate()
        if problems:
            for problem in problems:
                print("FAIL: " + problem, file=sys.stderr)
            return 1
        print(
            "gate OK: %d chars, single line, UTF-8" % len(ENTRY)
        )
        return 0
    # Gate self-check: the sealed scorer requires UTF-8 text of 1-200
    # characters, not only whitespace.
    problems = check_gate()
    if problems:
        raise SystemExit("; ".join(problems))
    text = ENTRY + "\n"
    path = output_path(argv)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    # Round-trip check: what we wrote must read back byte-identical,
    # as exactly one line whose content is the entry itself.
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw != text.encode("utf-8"):
        raise SystemExit("round-trip mismatch writing %s" % path)
    with open(path, "r", encoding="utf-8", newline="\n") as fh:
        lines = fh.read().splitlines()
    if len(lines) != 1 or lines[0] != ENTRY:
        raise SystemExit(
            "round-trip content mismatch: expected 1 line equal to ENTRY"
        )
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
