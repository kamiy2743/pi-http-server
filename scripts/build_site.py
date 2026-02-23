#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ORDERED_RE = re.compile(r"^\d+\.\s+")
FENCE_RE = re.compile(r"^```([a-zA-Z0-9_+-]*)\s*$")
HEADING_ID_RE = re.compile(r"^(.*?)\s*\{#([A-Za-z0-9_-]+)\}\s*$")


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug or "section"


def render_inline(text: str) -> str:
    placeholders: list[str] = []

    def add_placeholder(snippet: str, kind: str) -> str:
        placeholders.append(snippet)
        return f"\x00{kind}{len(placeholders)-1}\x00"

    def code_repl(match: re.Match[str]) -> str:
        return add_placeholder(f"<code>{html.escape(match.group(1))}</code>", "CODE")

    def image_repl(match: re.Match[str]) -> str:
        alt = html.escape(match.group(1), quote=True)
        src = html.escape(match.group(2), quote=True)
        return add_placeholder(f'<img src="{src}" alt="{alt}" />', "IMG")

    def link_repl(match: re.Match[str]) -> str:
        href = html.escape(match.group(2), quote=True)
        label = html.escape(match.group(1))
        return add_placeholder(f'<a href="{href}">{label}</a>', "LINK")

    text = re.sub(r"`([^`]+)`", code_repl, text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_repl, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    # Allow inline <br> tags and normalize trailing whitespace after them.
    def br_repl(match: re.Match[str]) -> str:
        return add_placeholder("<br />", "BR")

    text = re.sub(r"<br\s*/?>\s*", br_repl, text, flags=re.IGNORECASE)

    text = html.escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)

    for i, snippet in enumerate(placeholders):
        text = text.replace(f"\x00CODE{i}\x00", snippet)
        text = text.replace(f"\x00IMG{i}\x00", snippet)
        text = text.replace(f"\x00LINK{i}\x00", snippet)
        text = text.replace(f"\x00BR{i}\x00", snippet)
    return text


def render_markdown(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    out: list[str] = []
    i = 0

    def append_paragraph(paragraph_lines: list[str]) -> None:
        if not paragraph_lines:
            return
        # Preserve markdown line breaks as <br /> within a paragraph.
        text = "<br />\n".join(line.strip() for line in paragraph_lines).strip()
        if text:
            out.append(f"<p>{render_inline(text)}</p>")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            out.append("<hr />")
            i += 1
            continue

        fence_match = FENCE_RE.match(stripped)
        if fence_match:
            lang = fence_match.group(1)
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            class_attr = f' class="language-{lang}"' if lang else ""
            code_html = html.escape("\n".join(code_lines))
            out.append(f"<pre><code{class_attr}>{code_html}</code></pre>")
            continue

        if stripped.startswith("<"):
            raw_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip():
                raw_lines.append(lines[i])
                i += 1
            out.append("\n".join(raw_lines))
            continue

        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            heading_id = None
            id_match = HEADING_ID_RE.match(text)
            if id_match:
                text = id_match.group(1).strip()
                heading_id = id_match.group(2)
            elif level <= 2:
                heading_id = slugify(text)
            id_attr = f' id="{heading_id}"' if heading_id else ""
            out.append(f"<h{level}{id_attr}>{render_inline(text)}</h{level}>")
            i += 1
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].lstrip())
                i += 1
            quote_text = " ".join(quote_lines).strip()
            out.append(f"<blockquote><p>{render_inline(quote_text)}</p></blockquote>")
            continue

        if stripped.startswith(("- ", "* ")):
            items: list[str] = []
            while i < len(lines):
                current = lines[i].strip()
                if not current or not current.startswith(("- ", "* ")):
                    break
                items.append(current[2:].strip())
                i += 1
            out.append("<ul>")
            for item in items:
                out.append(f"  <li>{render_inline(item)}</li>")
            out.append("</ul>")
            continue

        if ORDERED_RE.match(stripped):
            items = []
            while i < len(lines):
                current = lines[i].strip()
                if not current or not ORDERED_RE.match(current):
                    break
                items.append(ORDERED_RE.sub("", current, count=1).strip())
                i += 1
            out.append("<ol>")
            for item in items:
                out.append(f"  <li>{render_inline(item)}</li>")
            out.append("</ol>")
            continue

        paragraph_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i]
            next_stripped = next_line.strip()
            if not next_stripped:
                break
            if (
                next_stripped.startswith("<")
                or next_stripped.startswith(">") 
                or next_stripped.startswith(("- ", "* "))
                or ORDERED_RE.match(next_stripped)
                or HEADING_RE.match(next_stripped)
                or FENCE_RE.match(next_stripped)
                or next_stripped == "---"
            ):
                break
            paragraph_lines.append(next_line)
            i += 1
        append_paragraph(paragraph_lines)

    return "\n".join(out)


def inject_article(template_html: str, article_html: str) -> str:
    replacement = (
        '    <main class="article">\n'
        '      <!-- Generated from content/article.md by scripts/build_site.py -->\n'
        f'{indent(article_html, "      ")}\n'
        '    </main>'
    )
    updated, count = re.subn(
        r"^\s*<main class=\"article\">.*?</main>",
        replacement,
        template_html,
        count=1,
        flags=re.DOTALL | re.MULTILINE,
    )
    if count != 1:
        raise ValueError("Could not find <main class=\"article\">...</main> in public/index.html")
    return updated


def indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line else prefix.rstrip() for line in text.splitlines())


def main() -> int:
    parser = argparse.ArgumentParser(description="Build public/index.html from Markdown article content.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root (defaults to repository root).",
    )
    args = parser.parse_args()

    root = args.root
    article_path = root / "content" / "article.md"
    html_path = root / "public" / "index.html"

    if not article_path.exists():
        print(f"Missing article source: {article_path}", file=sys.stderr)
        return 1
    if not html_path.exists():
        print(f"Missing HTML target/template: {html_path}", file=sys.stderr)
        return 1

    markdown_text = article_path.read_text(encoding="utf-8")
    article_html = render_markdown(markdown_text)
    current_html = html_path.read_text(encoding="utf-8")
    updated_html = inject_article(current_html, article_html)

    html_path.write_text(updated_html + ("\n" if not updated_html.endswith("\n") else ""), encoding="utf-8")
    print(f"Built {html_path} from {article_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
