#!/usr/bin/env python3
"""WordPress XML → Markdoc 変換スクリプト"""

import re
import xml.etree.ElementTree as ET

XML_PATH = 'WordPress.2026-04-23.xml'

NS = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
}

# 変換対象ページ: slug → 出力ファイルパス
TARGETS = {
    'about':       None,           # about.astro に直接埋め込む
    'boshu':       'src/content/singletons/recruitment.mdoc',
    'nittei2015':  'src/content/singletons/schedule.mdoc',
    'concertinfo': 'src/content/singletons/concert.mdoc',
}


def extract_pages(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    pages = {}
    for item in root.iter('item'):
        post_type = item.find('wp:post_type', NS)
        slug = item.find('wp:post_name', NS)
        if post_type is not None and post_type.text == 'page' and slug is not None:
            if slug.text in TARGETS:
                content = item.find('content:encoded', NS)
                pages[slug.text] = content.text if content is not None and content.text else ''
    return pages


def clean_html(html):
    """WordPress HTML をクリーンアップ"""
    # HTML コメント（<!--...-->）を削除
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    # WordPress ショートコードを削除
    html = re.sub(r'\[contact-form-7[^\]]*\]', '', html)
    html = re.sub(r'\[[^\]]+\]', '', html)
    # &nbsp; → スペース
    html = html.replace('&nbsp;', ' ')
    return html


def html_to_markdoc(html):
    """HTML をシンプルな Markdoc (Markdown) に変換"""
    html = clean_html(html)

    # <blockquote> ラッパーを除去（中身だけ残す）
    html = re.sub(r'</?blockquote[^>]*>', '', html)

    # <hr /> → ---
    html = re.sub(r'<hr\s*/?>', '\n\n---\n\n', html)

    # <strong> → **
    html = re.sub(r'<strong>(.*?)</strong>', r'**\1**', html, flags=re.DOTALL)
    html = re.sub(r'<b>(.*?)</b>', r'**\1**', html, flags=re.DOTALL)
    html = re.sub(r'<em>(.*?)</em>', r'*\1*', html, flags=re.DOTALL)

    # <a href="...">text</a> → [text](href)
    html = re.sub(
        r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
        lambda m: f'[{m.group(2).strip()}]({m.group(1)})',
        html, flags=re.DOTALL
    )

    # <img ...> → ![](src)
    html = re.sub(
        r'<img[^>]*src=["\']([^"\']*)["\'][^>]*/?>',
        lambda m: f'![]({m.group(1)})',
        html
    )

    # <h2> → ##
    html = re.sub(r'<h2[^>]*>(.*?)</h2>', lambda m: f'\n\n## {_strip_tags(m.group(1))}\n\n', html, flags=re.DOTALL)
    # <h3> → ###
    html = re.sub(r'<h3[^>]*>(.*?)</h3>', lambda m: f'\n\n### {_strip_tags(m.group(1))}\n\n', html, flags=re.DOTALL)
    # <h4> → ####
    html = re.sub(r'<h4[^>]*>(.*?)</h4>', lambda m: f'\n\n#### {_strip_tags(m.group(1))}\n\n', html, flags=re.DOTALL)
    # <h5>, <h6> → 太字段落（WordPress で装飾目的で誤用されているため）
    html = re.sub(r'<h[56][^>]*>(.*?)</h[56]>', lambda m: f'\n\n{_strip_tags(m.group(1))}\n\n', html, flags=re.DOTALL)

    # <ul><li>...</li></ul> → - ...
    def convert_list(m):
        items = re.findall(r'<li[^>]*>(.*?)</li>', m.group(0), re.DOTALL)
        return '\n' + '\n'.join(f'- {_strip_tags(item).strip()}' for item in items) + '\n'
    html = re.sub(r'<ul[^>]*>.*?</ul>', convert_list, html, flags=re.DOTALL)

    # <p> → 段落
    html = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: f'\n\n{_strip_tags(m.group(1)).strip()}\n\n', html, flags=re.DOTALL)

    # 残ったタグを除去
    html = _strip_tags(html)

    # 連続する空行を2行に整理
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html.strip()


def _strip_tags(text):
    """HTMLタグを除去し、インラインの span style 等を除去"""
    # <span style="...">text</span> → text
    text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)
    # 残りのHTMLタグを除去
    text = re.sub(r'<[^>]+>', '', text)
    return text


def write_mdoc(path, content_md, frontmatter=''):
    full = f'---\n{frontmatter}---\n{content_md}\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(full)
    print(f'  → {path} に書き出しました')


def main():
    print(f'{XML_PATH} を解析中...')
    pages = extract_pages(XML_PATH)

    for slug, out_path in TARGETS.items():
        html = pages.get(slug, '')
        if not html:
            print(f'[SKIP] {slug}: コンテンツなし')
            continue

        md = html_to_markdoc(html)
        print(f'\n[{slug}] 変換完了（{len(md)} 文字）')

        if out_path is None:
            # about ページは標準出力に表示
            print('--- about.astro 用コンテンツ (HTML) ---')
            print(clean_html(html)[:500] + '...')
        elif slug == 'boshu':
            write_mdoc(out_path, md, frontmatter='isRecruiting: true\n')
        else:
            write_mdoc(out_path, md)


if __name__ == '__main__':
    main()
