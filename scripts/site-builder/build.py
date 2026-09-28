#!/usr/bin/env python3
"""Validate and copy the static documentation site without third-party packages."""
import json
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SRC, OUT = ROOT / 'site', ROOT / 'dist'
CONFIG = json.loads((ROOT / 'site.config.json').read_text())

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.has_title = False
        self.has_h1 = False
        self.has_description = False
        self.images_without_alt = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title': self.has_title = True
        if tag == 'h1': self.has_h1 = True
        if tag == 'meta' and a.get('name') == 'description': self.has_description = True
        if 'id' in a: self.ids.add(a['id'])
        if tag == 'img' and 'alt' not in a: self.images_without_alt += 1
        for key in ('href', 'src'):
            if key in a: self.links.append(a[key])

def validate():
    errors = []
    for route in CONFIG['pages']:
        page = SRC / route.lstrip('/') / 'index.html'
        if not page.is_file():
            errors.append(f'Missing route: {route}')
            continue
        parser = Page()
        parser.feed(page.read_text())
        if not all((parser.has_title, parser.has_h1, parser.has_description)):
            errors.append(f'Missing title, h1, or description: {page}')
        if parser.images_without_alt: errors.append(f'Missing alt text: {page}')
        for link in parser.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc or link.startswith(('mailto:', 'tel:')): continue
            if parts.path.startswith('/'):
                target = SRC / parts.path.lstrip('/')
            else:
                target = page.parent / parts.path
            if target.is_dir(): target /= 'index.html'
            if not target.exists(): errors.append(f'Broken local link: {page}: {link}')
            if parts.fragment:
                linked_page = target if target.suffix == '.html' else page
                if linked_page.exists() and linked_page.suffix == '.html':
                    p = Page(); p.feed(linked_page.read_text())
                    if parts.fragment not in p.ids: errors.append(f'Missing anchor: {page}: {link}')
    return errors

if __name__ == '__main__':
    failures = validate()
    if failures:
        raise SystemExit('\n'.join(failures))
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    print(f'PASS: {len(CONFIG["pages"])} routes and local assets; output: {OUT}')
