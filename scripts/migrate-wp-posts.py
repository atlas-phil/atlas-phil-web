#!/usr/bin/env python3
"""Migrate WordPress posts to Keystatic posts collection."""

import os
import re
import xml.etree.ElementTree as ET

WP_XML = os.path.join(os.path.dirname(__file__), '..', 'WordPress.2026-04-23.xml')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'posts')

CATEGORY_MAP = {
    '【団員にきいてみた】シリーズ': 'interview',
    '本番レポート': 'concert-report',
    '団員ブログ': 'member-blog',
    '団員の愉快な日常': 'member-blog',
    'お知らせ': 'member-blog',
    '未分類': 'member-blog',
}
CATEGORY_PRIORITY = ['interview', 'concert-report', 'member-blog']


def html_to_markdown(html: str) -> str:
    if not html:
        return ''

    # Remove HTML comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    # Remove WP shortcodes
    html = re.sub(r'\[/?[a-zA-Z_-]+[^\]]*\]', '', html)

    # Convert block-level elements by adding newlines before processing inline
    # Headings
    html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n\n## \1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n\n### \1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n\n#### \1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<h5[^>]*>(.*?)</h5>', r'\n\n\1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<h6[^>]*>(.*?)</h6>', r'\n\n\1\n\n', html, flags=re.DOTALL)

    # Paragraphs and divs
    html = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\n\1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*>(.*?)</div>', r'\n\n\1\n\n', html, flags=re.DOTALL)

    # Blockquote
    def convert_blockquote(m):
        inner = m.group(1).strip()
        lines = inner.split('\n')
        return '\n\n' + '\n'.join(f'> {l}' if l.strip() else '>' for l in lines) + '\n\n'
    html = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', convert_blockquote, html, flags=re.DOTALL)

    # Lists
    def convert_list_items(html_inner, ordered=False):
        def convert_li(m):
            content = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            prefix = '1.' if ordered else '-'
            return f'\n{prefix} {content}'
        return re.sub(r'<li[^>]*>(.*?)</li>', convert_li, html_inner, flags=re.DOTALL)

    def convert_ul(m):
        return '\n\n' + convert_list_items(m.group(1), ordered=False) + '\n\n'
    def convert_ol(m):
        return '\n\n' + convert_list_items(m.group(1), ordered=True) + '\n\n'

    html = re.sub(r'<ul[^>]*>(.*?)</ul>', convert_ul, html, flags=re.DOTALL)
    html = re.sub(r'<ol[^>]*>(.*?)</ol>', convert_ol, html, flags=re.DOTALL)
    # Remaining li tags
    html = re.sub(r'<li[^>]*>(.*?)</li>', r'\n- \1', html, flags=re.DOTALL)

    # Definition lists
    html = re.sub(r'<dl[^>]*>(.*?)</dl>', r'\n\n\1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<dt[^>]*>(.*?)</dt>', r'\n\n\1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<dd[^>]*>(.*?)</dd>', r'\n\1\n', html, flags=re.DOTALL)

    # Pre/code
    html = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\n\n\1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html, flags=re.DOTALL)

    # Figure/figcaption
    html = re.sub(r'<figcaption[^>]*>(.*?)</figcaption>', r'\n*\1*\n', html, flags=re.DOTALL)
    html = re.sub(r'<figure[^>]*>(.*?)</figure>', r'\n\n\1\n\n', html, flags=re.DOTALL)

    # HR
    html = re.sub(r'<hr\s*/?>', '\n\n---\n\n', html)

    # Inline: images (before links so linked images work)
    def convert_img(m):
        attrs = m.group(1)
        src_m = re.search(r'src="([^"]*)"', attrs)
        alt_m = re.search(r'alt="([^"]*)"', attrs)
        src = src_m.group(1) if src_m else ''
        alt = alt_m.group(1) if alt_m else ''
        return f'![{alt}]({src})' if src else ''
    html = re.sub(r'<img([^>]*)/?>', convert_img, html)

    # Links: <a href="...">text</a>
    def convert_link(m):
        attrs = m.group(1)
        inner = m.group(2).strip()
        href_m = re.search(r'href="([^"]*)"', attrs)
        href = href_m.group(1) if href_m else ''
        if not inner or not href:
            return inner
        return f'[{inner}]({href})'
    html = re.sub(r'<a([^>]*)>(.*?)</a>', convert_link, html, flags=re.DOTALL)

    # Inline formatting
    html = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html, flags=re.DOTALL)
    html = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html, flags=re.DOTALL)
    html = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', html, flags=re.DOTALL)
    html = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', html, flags=re.DOTALL)

    # Span (remove tag, keep content)
    html = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', html, flags=re.DOTALL)

    # BR
    html = re.sub(r'<br\s*/?>', '\n', html)

    # Remove remaining HTML tags
    html = re.sub(r'<[^>]+>', '', html)

    # Decode HTML entities
    html = html.replace('&amp;', '&')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&quot;', '"')
    html = html.replace('&#8220;', '“')
    html = html.replace('&#8221;', '”')
    html = html.replace('&#8216;', '‘')
    html = html.replace('&#8217;', '’')
    html = html.replace('&#8230;', '…')
    html = html.replace('&#8211;', '–')
    html = html.replace('&#8212;', '—')
    html = html.replace('&nbsp;', ' ')
    html = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), html)

    # Normalize whitespace
    # Collapse multiple spaces on a line (but not newlines)
    lines = html.split('\n')
    lines = [re.sub(r'[ \t]+', ' ', line).rstrip() for line in lines]
    html = '\n'.join(lines)

    # Collapse 3+ consecutive newlines → 2
    html = re.sub(r'\n{3,}', '\n\n', html)
    html = html.strip()

    return html


def map_category(wp_cats: list) -> str:
    mapped = set()
    for cat in wp_cats:
        if cat in CATEGORY_MAP:
            mapped.add(CATEGORY_MAP[cat])
    for priority_cat in CATEGORY_PRIORITY:
        if priority_cat in mapped:
            return priority_cat
    return 'member-blog'


def escape_yaml_string(s: str) -> str:
    if any(c in s for c in ('"', "'", ':', '#', '\n', '[', ']', '{', '}')):
        s = s.replace('"', '\\"')
        return f'"{s}"'
    return s


def main():
    ns = {
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
    }

    tree = ET.parse(WP_XML)
    root = tree.getroot()
    items = root.findall('.//item')

    posts = [
        i for i in items
        if (
            i.find('wp:post_type', ns) is not None
            and i.find('wp:post_type', ns).text == 'post'
            and i.find('wp:status', ns) is not None
            and i.find('wp:status', ns).text == 'publish'
        )
    ]

    print(f'Found {len(posts)} published posts')
    os.makedirs(OUT_DIR, exist_ok=True)

    created = 0
    skipped = 0

    for post in posts:
        title = (post.find('title').text or '').strip()
        wp_slug = (post.find('wp:post_name', ns).text or '').strip()
        date_str = (post.find('wp:post_date', ns).text or '')[:10]
        raw_content = post.find('content:encoded', ns).text or ''

        wp_cats = [c.text for c in post.findall('category') if c.get('domain') == 'category']
        category = map_category(wp_cats)

        if not wp_slug:
            wp_slug = re.sub(r'[^\w\-]', '-', title)[:50].strip('-') or f'post-{created}'

        slug_dir = os.path.join(OUT_DIR, wp_slug)
        out_file = os.path.join(slug_dir, 'index.mdoc')

        if os.path.exists(out_file):
            skipped += 1
            continue

        markdown_content = html_to_markdown(raw_content)

        title_yaml = escape_yaml_string(title)
        frontmatter = (
            f'---\n'
            f'title: {title_yaml}\n'
            f'publishedDate: {date_str}\n'
            f'category: {category}\n'
            f'---\n'
        )
        file_content = frontmatter + markdown_content + '\n'

        os.makedirs(slug_dir, exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(file_content)

        print(f'  {date_str} [{category}] {wp_slug}')
        created += 1

    print(f'\nDone: {created} created, {skipped} skipped')


if __name__ == '__main__':
    main()
