#!/usr/bin/env python3
"""Send a generated A-share global review Markdown file as styled HTML email.

Credentials are read from environment variables. Do not hard-code secrets.
"""

from __future__ import annotations

import argparse
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from pathlib import Path


def _is_table_start(lines: list[str], idx: int) -> bool:
    return (
        idx + 1 < len(lines)
        and lines[idx].strip().startswith("|")
        and lines[idx + 1].strip().startswith("|")
        and "---" in lines[idx + 1]
    )


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue

        if line.startswith("# "):
            blocks.append(f"<h1>{escape(line[2:].strip())}</h1>")
            i += 1
            continue

        if line.startswith("◆ "):
            blocks.append(f"<h2>{escape(line.strip())}</h2>")
            i += 1
            continue

        if _is_table_start(lines, i):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1

            parts = ['<div class="table-wrap"><table><thead><tr>']
            parts.extend(f"<th>{escape(h)}</th>" for h in header)
            parts.append("</tr></thead><tbody>")
            for row in rows:
                parts.append("<tr>")
                for cell in row:
                    cls = ' class="num"' if re.search(r"[+\-]?\d", cell) else ""
                    parts.append(f"<td{cls}>{escape(cell)}</td>")
                parts.append("</tr>")
            parts.append("</tbody></table></div>")
            blocks.append("".join(parts))
            continue

        if line.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append("<ul>" + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            blocks.append("<ol>" + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ol>")
            continue

        para = [line]
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not lines[i].startswith("# ")
            and not lines[i].startswith("◆ ")
            and not lines[i].strip().startswith("|")
            and not lines[i].strip().startswith("- ")
            and not re.match(r"^\d+\.\s+", lines[i].strip())
        ):
            para.append(lines[i].strip())
            i += 1
        text = escape(" ".join(para))
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        blocks.append(f"<p>{text}</p>")

    style = """
body{margin:0;background:#f5f7fb;color:#151922;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Arial,sans-serif;line-height:1.65}
.container{max-width:920px;margin:0 auto;padding:20px 14px 36px}
.card{background:#fff;border:1px solid #e6e8ef;border-radius:12px;padding:22px;box-shadow:0 2px 10px rgba(25,31,44,.04)}
h1{font-size:24px;line-height:1.3;margin:0 0 14px;color:#0f172a}
h2{font-size:18px;margin:26px 0 10px;padding-left:10px;border-left:4px solid #2563eb;color:#111827}
p{margin:10px 0;font-size:15px}
ul,ol{padding-left:22px;margin:10px 0}
li{margin:6px 0;font-size:15px}
.table-wrap{overflow-x:auto;margin:12px 0;border:1px solid #e5e7eb;border-radius:10px}
table{width:100%;border-collapse:collapse;min-width:680px;background:#fff}
th{background:#f1f5f9;color:#111827;font-weight:700}
th,td{border-bottom:1px solid #e5e7eb;padding:8px 10px;text-align:left;vertical-align:top;font-size:13px}
tr:last-child td{border-bottom:none}
td.num{text-align:right;white-space:nowrap}
code{background:#eef2ff;color:#1d4ed8;border-radius:4px;padding:1px 4px}
.note{margin-top:22px;padding:12px 14px;background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;color:#7c2d12;font-size:14px}
@media(max-width:600px){.container{padding:10px 8px 24px}.card{padding:15px;border-radius:10px}h1{font-size:21px}h2{font-size:16px}p,li{font-size:14px}th,td{font-size:12px;padding:7px 8px}table{min-width:620px}}
"""
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<style>{style}</style></head><body><div class=\"container\"><div class=\"card\">"
        + "".join(blocks)
        + '<div class="note">本邮件由 a-share-global-review skill 生成；内容为复盘和观察计划，不构成投资建议。</div>'
        + "</div></div></body></html>"
    )


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Markdown review file path")
    parser.add_argument("--subject", default=None, help="Email subject")
    args = parser.parse_args()

    path = Path(args.file)
    markdown = path.read_text(encoding="utf-8")
    html = markdown_to_html(markdown)

    host = os.environ.get("A_SHARE_REVIEW_SMTP_HOST", "smtp.qq.com").strip()
    port = int(os.environ.get("A_SHARE_REVIEW_SMTP_PORT", "465"))
    user = required_env("A_SHARE_REVIEW_SMTP_USER")
    password = required_env("A_SHARE_REVIEW_SMTP_PASS")
    recipients = [x.strip() for x in required_env("A_SHARE_REVIEW_TO").split(",") if x.strip()]
    if not recipients:
        raise SystemExit("A_SHARE_REVIEW_TO has no valid recipients")

    subject = args.subject or path.stem
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL(host, port, timeout=30) as smtp:
        smtp.login(user, password)
        smtp.sendmail(user, recipients, msg.as_string())

    print(f"sent {path} to {', '.join(recipients)}")


if __name__ == "__main__":
    main()
