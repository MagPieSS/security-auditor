"""Mask secrets in text before anyone sees it.

Reads text on stdin and prints it with anything that looks like a secret
replaced by **** plus its last 4 characters. The security-auditor agent
pipes every secret search through this so a full secret never lands in a
transcript or a report.

Usage:
    git grep -nI "API_KEY" | python -I mask_secrets.py

It masks too much on purpose. A hidden identifier costs a second look;
a printed key costs a rotation.
"""

import re
import sys

KEEP = 4

# Values shorter than this show no characters at all. Showing the last
# 4 of a 6-character password would print most of it.
MIN_TO_SHOW_TAIL = 12

# "postgres://user:hunter22@host". The password is short and has no
# secret-sounding name, so the other two rules miss it.
URL_CREDENTIALS = re.compile(r"(\w+://[^:/\s@]+:)([^@\s]+)(@)")

# A value assigned to a name that says it is secret, however short.
# "password = hunter22" has no long token for TOKEN to catch.
NAMED = re.compile(
    r"((?:key|secret|token|passw(?:or)?d|pwd|private|credential|auth)\w*[\"']?\s*[:=]\s*[\"']?)"
    r"([^\"'\s,;]{5,})",
    re.IGNORECASE,
)

# Code that reads a value from the environment instead of holding one.
ENV_READ = re.compile(r"(os\.environ|os\.getenv|process\.env|import\.meta\.env|Deno\.env|getenv\(|env\()")

# Any long run of key-like characters. Only masked if it mixes letters
# and digits (see hide_token), which real keys do and plain words don't.
TOKEN = re.compile(r"[A-Za-z0-9_\-+/=]{20,}")

# grep -n output: "path:12:text" or "path:12-text". The location is
# split off first so it stays readable.
LOCATION = re.compile(r"^([^:\s][^:]*:\d+[:-])(.*)$")


def hide(value):
    if len(value) < MIN_TO_SHOW_TAIL:
        return "****"
    return "****" + value[-KEEP:]


def hide_token(match):
    s = match.group(0)
    has_letter = re.search(r"[A-Za-z]", s) is not None
    has_digit = re.search(r"\d", s) is not None
    if not (has_letter and has_digit):
        return s
    return hide(s)


def hide_named(match):
    value = match.group(2)
    # "API_KEY = os.environ.get(" is the fix, not a leak. Hiding it
    # makes every fix diff unreadable. Matched by an exact list so a
    # real password can't slip through by looking like code.
    if ENV_READ.match(value):
        return match.group(0)
    return match.group(1) + hide(value)


def mask(text):
    text = URL_CREDENTIALS.sub(lambda m: m.group(1) + hide(m.group(2)) + m.group(3), text)
    text = NAMED.sub(hide_named, text)
    return TOKEN.sub(hide_token, text)


def mask_line(line):
    m = LOCATION.match(line)
    if m is None:
        return mask(line)
    return m.group(1) + mask(m.group(2))


def main():
    # Windows consoles default to a legacy code page. A byte it can't
    # decode must not crash the filter halfway and drop the rest.
    sys.stdin.reconfigure(errors="replace")
    sys.stdout.reconfigure(errors="replace")
    for line in sys.stdin:
        print(mask_line(line.rstrip("\n")))


if __name__ == "__main__":
    main()
