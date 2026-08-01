#!/usr/bin/env python3
"""Render a GitHub Issue into a Build Log post inside index.html.

Stdlib only. Invoked by .github/workflows/publish-post.yml with the issue
passed via environment variables (never shell-interpolated):

  POST_TITLE  issue title ("post: ..." prefix is stripped)
  POST_BODY   issue body, GitHub-flavored markdown (small subset rendered)
  POST_URL    html_url of the issue
  POST_ISSUE  issue number

Security posture:
  - All text is HTML-escaped first; only a tiny, deliberate markdown subset
    is then re-introduced (paragraphs, lists, fenced/inline code, bold,
    https links).
  - Anything shaped like an email address is redacted. This site is kept
    email-free on purpose.
"""

import html
import os
import re
import sys
from datetime import datetime, timezone

INDEX = os.path.join(os.path.dirname(__file__), "..", "..", "index.html")
START = "<!-- POSTS:START -->"
END = "<!-- POSTS:END -->"

# local-part '@' domain '.' tld  (built piecewise so this file itself
# never contains an email-shaped literal)
EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+-]+" + "@" + r"[A-Za-z0-9.-]+" + r"\.[A-Za-z]{2,}"
)


def redact(text: str) -> str:
    return EMAIL_RE.sub("[redacted]", text)


def render_inline(escaped: str) -> str:
    """Inline markdown on already-escaped text: `code`, **bold**, [t](https://...)."""
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(
        r"\[([^\]]+)\]\((https://[^)\s]+)\)",
        r'<a href="\2">\1</a>',
        out,
    )
    return out


def render_markdown(body: str) -> str:
    """Minimal, escape-first markdown renderer."""
    parts = re.split(r"```[A-Za-z0-9_+-]*\r?\n(.*?)```", body, flags=re.S)
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # fenced code block
            out.append(
                "<pre><code>" + html.escape(part.rstrip()) + "</code></pre>"
            )
            continue
        for block in re.split(r"\n\s*\n", part.strip()):
            if not block.strip():
                continue
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            if all(ln.startswith("- ") for ln in lines):
                items = "".join(
                    "<li>" + render_inline(html.escape(ln[2:])) + "</li>"
                    for ln in lines
                )
                out.append("<ul>" + items + "</ul>")
            else:
                out.append(
                    "<p>" + render_inline(html.escape(" ".join(lines))) + "</p>"
                )
    return "\n          ".join(out)


def main() -> int:
    title = os.environ.get("POST_TITLE", "").strip()
    body = os.environ.get("POST_BODY", "") or ""
    url = os.environ.get("POST_URL", "").strip()
    issue = os.environ.get("POST_ISSUE", "").strip()

    title = re.sub(r"^post:\s*", "", title, flags=re.I).strip() or "untitled"
    title = redact(title)
    body = redact(body)
    if not re.fullmatch(r"https://github\.com/[\w./-]+", url):
        url = ""
    if not issue.isdigit():
        issue = ""

    with open(INDEX, encoding="utf-8") as fh:
        src = fh.read()
    if START not in src or END not in src:
        print("post markers missing from index.html", file=sys.stderr)
        return 1

    region = src.split(START, 1)[1].split(END, 1)[0]
    run_no = region.count('<article class="post') + 1
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    provenance = (
        f' &middot; <a href="{url}">issue #{issue}</a>' if url and issue else ""
    )
    chips = "".join(
        f'<span class="st" style="--pd:{d}s">{name}</span>'
        + ('<span class="sep">&rarr;</span>' if name != "deploy" else "")
        for name, d in [
            ("issue", "0"),
            ("action", "0.3"),
            ("render", "0.6"),
            ("commit", "0.9"),
            ("deploy", "1.2"),
        ]
    )

    post = f"""{START}
      <article class="post reveal">
        <div class="meta mono"><span class="ok">&#9679;</span> run #{run_no:03d} &middot; {date}{provenance}</div>
        <h3>{render_inline(html.escape(title))}</h3>
        <div class="body">
          {render_markdown(body)}
        </div>
        <div class="pipe mono" aria-hidden="true">{chips}</div>
      </article>"""

    updated = src.replace(START, post, 1)

    # Belt and braces: never let an email-shaped string reach the page.
    with open(INDEX, "w", encoding="utf-8") as fh:
        fh.write(redact(updated))

    print(f"published run #{run_no:03d}: {title!r} ({len(body)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
