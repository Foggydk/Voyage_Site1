#!/usr/bin/env python3
"""Transform exported HTML into semantic multi-page site."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    ("_4", "tours", "tours"),
    ("_6", "treatment", "treatment"),
    ("_5", "destinations", "destinations"),
    ("_3", "about", "about"),
    ("_1", "account", "account"),
    ("_2", "login", None),
]

NAV_ITEMS = [
    ("Туры", "tours"),
    ("Лечение", "treatment"),
    ("Направления", "destinations"),
    ("О компании", "about"),
]

SITE_CSS = '<link href="../assets/css/site.css" rel="stylesheet"/>\n'

GLASS_RE = re.compile(
    r"\s*\.glass-card\s*\{[^}]+\}\s*",
    re.DOTALL,
)


def add_site_css(html: str) -> str:
    if "assets/css/site.css" in html:
        return html
    marker = '<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined'
    idx = html.find(marker)
    if idx == -1:
        return SITE_CSS + html
    end = html.find("/>", idx) + 2
    # after second material symbols link if duplicated
    next_link = html.find(marker, end)
    if next_link != -1:
        end = html.find("/>", next_link) + 2
    return html[:end] + "\n" + SITE_CSS + html[end:]


def strip_glass_from_style(html: str) -> str:
    return GLASS_RE.sub("\n        ", html)


def wire_footer_nav(html: str) -> str:
    for label, slug in NAV_ITEMS:
        html = html.replace(
            f'href="#">{label}</a>',
            f'href="../{slug}/">{label}</a>',
        )
    html = html.replace('href="#">О нас</a>', 'href="../about/">О нас</a>')
    return html


def wire_logo(html: str) -> str:
    # Header logo block -> link to tours
    if "travel_explore" in html and 'href="../tours/"' not in html.split("travel_explore")[0][-200:]:
        html = re.sub(
            r'<div class="font-headline-md text-headline-md text-error font-extrabold flex items-center gap-2">',
            r'<a class="font-headline-md text-headline-md text-error font-extrabold flex items-center gap-2 hover:opacity-90 transition-opacity" href="../tours/">',
            html,
            count=1,
        )
        html = html.replace(
            "<span>Вояж-Тур</span>\n</div>",
            "<span>Вояж-Тур</span>\n</a>",
            1,
        )
    html = re.sub(
        r'<div class="font-headline-md text-headline-md text-error(?: dark:text-error-container)? font-extrabold(?: tracking-tight)?">\s*Вояж-Тур\s*</div>',
        r'<a class="font-headline-md text-headline-md text-error dark:text-error-container font-extrabold tracking-tight hover:opacity-90 transition-opacity" href="../tours/">Вояж-Тур</a>',
        html,
        count=1,
    )
    html = re.sub(
        r'<div class="text-headline-md font-headline-md font-extrabold text-error dark:text-error-container">Вояж-Тур</div>',
        r'<a class="text-headline-md font-headline-md font-extrabold text-error dark:text-error-container hover:opacity-90 transition-opacity" href="../tours/">Вояж-Тур</a>',
        html,
        count=1,
    )
    html = html.replace(
        '<span class="font-headline-md text-headline-md text-error font-extrabold">Вояж-Тур</span>',
        '<a class="font-headline-md text-headline-md text-error font-extrabold hover:opacity-90 transition-opacity" href="../tours/">Вояж-Тур</a>',
        1,
    )
    # Login brand
    html = re.sub(
        r'(<div class="mb-sm">\s*<span class="text-headline-md font-headline-md font-extrabold text-error">Вояж-Тур</span>\s*</div>)',
        r'<div class="mb-sm"><a class="text-headline-md font-headline-md font-extrabold text-error hover:opacity-90 transition-opacity" href="../tours/">Вояж-Тур</a></div>',
        html,
        count=1,
    )
    return html


def build_nav_link(label: str, slug: str, active: str) -> str:
    base = f'href="../{slug}/">{label}</a>'
    if slug == active:
        return (
            f'href="../{slug}/" aria-current="page" '
            f'class="text-error border-b-2 border-error pb-1">{label}</a>'
        )
    inactive_classes = [
        'class="font-body-md text-body-md text-on-surface-variant hover:text-error transition-colors"',
        'class="text-on-surface-variant hover:text-error transition-colors"',
        'class="text-label-md font-label-md text-on-surface-variant hover:text-primary transition-colors"',
    ]
    for cls in inactive_classes:
        marker = f'{cls} href="#">{label}</a>'
        if marker in f'...':  # noqa - unused
            pass
    return base


def wire_header_nav(html: str, active: str | None) -> str:
    """Replace nav links in header; set active state."""
    replacements = []
    for label, slug in NAV_ITEMS:
        inactive_pat = re.compile(
            rf'<a class="([^"]*)" href="#">{re.escape(label)}</a>'
        )

        def repl_inactive(m, s=slug, l=label):
            return f'<a class="{m.group(1)}" href="../{s}/">{l}</a>'

        html = inactive_pat.sub(repl_inactive, html)

    if active:
        for label, slug in NAV_ITEMS:
            if slug == active:
                # Promote to active styles (several header variants)
                patterns = [
                    (
                        rf'<a class="([^"]*)" href="../{slug}/">{label}</a>',
                        f'<a class="text-error border-b-2 border-error pb-1" href="../{slug}/" aria-current="page">{label}</a>',
                    ),
                    (
                        rf'<a class="font-body-md text-body-md text-on-surface-variant hover:text-error transition-colors" href="../{slug}/">{label}</a>',
                        f'<a class="font-body-md text-body-md text-error border-b-2 border-error pb-1" href="../{slug}/" aria-current="page">{label}</a>',
                    ),
                ]
                for pat, rep in patterns:
                    html = re.sub(pat, rep, html, count=1)
            else:
                # Demote previously active hardcoded links
                html = html.replace(
                    f'<a class="text-error border-b-2 border-error pb-1" href="../{slug}/">{label}</a>',
                    f'<a class="text-on-surface-variant hover:text-error transition-colors" href="../{slug}/">{label}</a>',
                )
                html = html.replace(
                    f'<a class="font-body-md text-body-md text-error border-b-2 border-error pb-1" href="#">{label}</a>',
                    f'<a class="font-body-md text-body-md text-on-surface-variant hover:text-error transition-colors" href="../{slug}/">{label}</a>',
                )

    # Account page nav (uses hover:text-primary)
    for label, slug in NAV_ITEMS:
        html = html.replace(
            f'<a class="text-label-md font-label-md text-on-surface-variant hover:text-primary transition-colors text-label-md font-label-md" href="#">{label}</a>',
            f'<a class="text-label-md font-label-md text-on-surface-variant hover:text-primary transition-colors" href="../{slug}/">{label}</a>',
        )
        html = html.replace(
            f'<a class="text-on-surface-variant hover:text-primary transition-colors text-label-md font-label-md" href="#">{label}</a>',
            f'<a class="text-on-surface-variant hover:text-primary transition-colors text-label-md font-label-md" href="../{slug}/">{label}</a>',
        )

    return html


def wire_account_button(html: str) -> str:
    html = re.sub(
        r'<button class="bg-error text-on-primary([^"]*)"([^>]*)>Личный кабинет</button>',
        r'<a class="btn btn-primary\1 font-label-md\2" href="../account/">Личный кабинет</a>',
        html,
    )
    html = re.sub(
        r'<button class="([^"]*bg-error text-on-primary[^"]*)"([^>]*)>\s*Личный кабинет\s*</button>',
        r'<a class="btn btn-primary px-md py-sm rounded-lg font-label-md text-label-md shadow-md" href="../account/">Личный кабинет</a>',
        html,
    )
    return html


def clean_btn_conflicts(html: str) -> str:
    """Remove Tailwind hovers that override .btn-primary styles."""
    for cls in (
        "hover:opacity-90",
        "active:scale-95",
        "active:scale-[0.98]",
        "hover:scale-105",
        "hover:scale-[1.02]",
        "transition-opacity",
        "transition-transform",
    ):
        html = re.sub(
            rf'(<a class="btn btn-primary[^"]*)\s*{re.escape(cls)}',
            r"\1",
            html,
        )
    html = re.sub(r'font-label-md(\s+font-label-md)+', "font-label-md", html)
    return html


def wire_account_page(html: str) -> str:
    html = html.replace(
        '<span class="text-label-md font-label-md text-error border-b-2 border-error pb-1">Личный кабинет</span>',
        '<a class="text-label-md font-label-md text-error border-b-2 border-error pb-1" href="../account/" aria-current="page">Личный кабинет</a>',
        1,
    )
    return html


def apply_btn_classes(html: str) -> str:
    subs = [
        (
            'class="bg-error text-on-primary px-md py-base rounded-lg font-label-md hover:opacity-90 transition-opacity active:scale-95"',
            'class="btn btn-primary px-md py-base rounded-lg font-label-md"',
        ),
        (
            'class="bg-error text-on-primary px-md py-xs rounded-lg font-label-md active:scale-95 transition-transform hover:opacity-90"',
            'class="btn btn-primary px-md py-xs rounded-lg font-label-md"',
        ),
        (
            'class="bg-error text-on-primary px-md py-sm rounded-lg font-label-md text-label-md hover:opacity-90 active:scale-95 transition-all shadow-md"',
            'class="btn btn-primary px-md py-sm rounded-lg font-label-md text-label-md shadow-md"',
        ),
        (
            'class="w-full bg-error text-on-primary py-sm rounded-lg font-label-md shadow-md hover:opacity-90 active:scale-95 transition-all"',
            'class="btn btn-primary w-full py-sm rounded-lg font-label-md shadow-md"',
        ),
        (
            'class="w-full h-14 bg-error text-white font-label-md text-label-md rounded-lg hover:bg-error/90 active:scale-95 transition-all shadow-md"',
            'class="btn btn-primary w-full h-14 font-label-md text-label-md rounded-lg shadow-md"',
        ),
        (
            'class="bg-error text-on-primary px-lg py-sm rounded-lg font-label-md text-label-md hover:scale-105 transition-transform"',
            'class="btn btn-primary px-lg py-sm rounded-lg font-label-md text-label-md"',
        ),
        (
            'class="bg-error text-on-primary px-md py-sm rounded-full font-label-md text-label-md flex items-center gap-xs shadow-lg"',
            'class="btn btn-primary px-md py-sm rounded-full font-label-md text-label-md flex items-center gap-xs shadow-lg"',
        ),
        (
            'class="bg-error text-on-primary p-3 rounded-lg hover:opacity-90 active:scale-95 transition-all"',
            'class="btn btn-primary p-3 rounded-lg"',
        ),
        (
            'class="bg-error text-on-primary px-lg py-md rounded-xl font-label-md shadow-lg hover:shadow-error/20 hover:scale-[1.02] transition-all"',
            'class="btn btn-primary px-lg py-md rounded-xl font-label-md shadow-lg"',
        ),
        (
            'class="w-full bg-error text-on-primary py-lg rounded-xl font-headline-md shadow-lg shadow-error/30 hover:shadow-error/40 active:scale-[0.98] transition-all"',
            'class="btn btn-primary w-full py-lg rounded-xl font-headline-md shadow-lg shadow-error/30"',
        ),
        (
            'class="bg-white/70 backdrop-blur-md border border-outline-variant/20 text-on-surface px-lg py-md rounded-xl font-label-md hover:bg-white transition-all"',
            'class="btn btn-ghost px-lg py-md rounded-xl font-label-md border border-outline-variant/20"',
        ),
    ]
    for old, new in subs:
        html = html.replace(old, new)
    # Hero CTA as <a>
    html = html.replace(
        '<a class="bg-error text-on-primary px-lg py-md rounded-xl font-label-md shadow-lg hover:shadow-error/20 hover:scale-[1.02] transition-all"',
        '<a class="btn btn-primary px-lg py-md rounded-xl font-label-md shadow-lg"',
    )
    return html


def add_login_redirect(html: str) -> str:
    if 'id="login-form"' in html or "login-form" in html:
        return html
    html = html.replace('<form action="#"', '<form id="login-form" action="#"')
    if "loginRedirect" in html:
        return html
    script = """
<script>
document.getElementById('login-form')?.addEventListener('submit', function (e) {
  e.preventDefault();
  window.location.href = '../account/';
});
</script>
"""
    return html.replace("</body>", script + "\n</body>")


def transform(src: Path, active: str | None) -> str:
    html = src.read_text(encoding="utf-8")
    html = add_site_css(html)
    html = strip_glass_from_style(html)
    html = wire_logo(html)
    html = wire_header_nav(html, active)
    html = wire_footer_nav(html)
    html = wire_account_button(html)
    html = apply_btn_classes(html)
    html = clean_btn_conflicts(html)
    if active == "account":
        html = wire_account_page(html)
    if active is None:
        html = add_login_redirect(html)
    return html


def main():
    for src_folder, dest_folder, active in PAGES:
        src = ROOT / src_folder / "code.html"
        dest_dir = ROOT / dest_folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "index.html"
        dest.write_text(transform(src, active), encoding="utf-8")
        print(f"Wrote {dest.relative_to(ROOT)}")

    index_html = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <meta http-equiv="refresh" content="0; url=tours/"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Вояж-Тур</title>
  <link href="assets/css/site.css" rel="stylesheet"/>
  <style>
    body { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #fcf8f8; color: #1c1b1b; }
    a { color: #ba1a1a; font-weight: 600; }
  </style>
</head>
<body>
  <p>Перенаправление на <a href="tours/">раздел туров</a>…</p>
</body>
</html>
"""
    (ROOT / "index.html").write_text(index_html, encoding="utf-8")
    print("Wrote index.html")


if __name__ == "__main__":
    main()
