#!/usr/bin/env python3
"""Build the practice notes and sitemap using the existing site header/footer."""
from pathlib import Path
from html import escape
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SITE = 'https://hiromeru-inc.com'
DATE = '2026-11-03'
ORG = {'@type':'Organization', '@id':SITE+'/#organization', 'name':'株式会社ヒロメル',
       'url':SITE+'/', 'logo':SITE+'/assets/hiromeru-logo.png', 'email':'contact@hiromeru-inc.com',
       'telephone':'+81-80-6051-1363', 'address':{'@type':'PostalAddress', 'addressCountry':'JP',
       'addressRegion':'東京都','addressLocality':'品川区','streetAddress':'戸越5-18-16-2F'},
       'description':'公式LINEのAI応対、営業メールの自動化、動画の切り抜き、業務へのAI導入を支援します。'}

def schema(graph):
    return '<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False)+'</script>'

home_path = ROOT/'index.html'
home = home_path.read_text()
home_schema = schema([ORG, {'@type':'WebSite','@id':SITE+'/#website','url':SITE+'/',
                            'name':'株式会社ヒロメル','publisher':{'@id':ORG['@id']},'inLanguage':'ja'}])
home = re.sub(r'\n?<!-- seo-schema -->.*?<!-- /seo-schema -->', '', home, flags=re.S)
home = home.replace('</head>','<!-- seo-schema -->'+home_schema+'<!-- /seo-schema -->\n</head>')
home_path.write_text(home)
head = home.split('<head>',1)[1].split('</head>',1)[0]
head = re.sub(r'<!-- seo-schema -->.*?<!-- /seo-schema -->','',head,flags=re.S)
header = home.split('<body>',1)[1].split('<main id="main">',1)[0]
footer = '<footer'+home.split('<footer',1)[1].split('</footer>',1)[0]+'</footer>'

def rooted(s):
    s = re.sub(r'(href|src)="assets/',r'\1="/assets/',s)
    return re.sub(r'href="#(?!main\b)([^"]+)"',r'href="/#\1"',s)

def page(path,title,description,content,graph):
    page_head = re.sub(r'<title>.*?</title>', '<title>'+escape(title)+'</title>', head)
    for key, value in [('description',description),('og:title',title),('og:description',description),('og:url',SITE+path)]:
        page_head = re.sub(r'(<meta (?:name|property)="'+re.escape(key)+r'" content=")[^"]*(")',lambda m:m[1]+escape(value,quote=True)+m[2],page_head)
    page_head = re.sub(r'(<link rel="canonical" href=")[^"]*(")',lambda m:m[1]+SITE+path+m[2],page_head)
    page_head = page_head.replace('content="website"','content="article"') if any(g.get('@type')=='BlogPosting' for g in graph) else page_head
    page_head = rooted(page_head)+'<link rel="stylesheet" href="/assets/notes-20261103.css">'+schema([ORG]+graph)
    rendered = '<!doctype html>\n<html lang="ja"><head>'+page_head+'</head><body>'+rooted(header)+'<main id="main" class="notes-main">'+content+'</main>'+rooted(footer)+'</body></html>\n'
    dst = ROOT/path.strip('/')/'index.html'
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(rendered)
    assert len(re.findall(r'<h1(?:\s|>)',rendered))==1, path
    assert '/Users/' not in rendered, path
    for payload in re.findall(r'<script type="application/ld\+json">(.*?)</script>',rendered,re.S): json.loads(payload)
    return rendered

articles = json.loads((ROOT/'src/notes/articles.json').read_text())
cards=[]
urls=[('/',DATE),('/notes/',max(a['date'] for a in articles))]
for a in articles:
    path='/notes/'+a['slug']+'/'
    body=(ROOT/'src/notes'/f"{a['slug']}.html").read_text()
    toc='<nav class="notes-toc" aria-label="目次"><b>この記事の内容</b><ul>'+''.join(f'<li><a href="#s{i+1}">{escape(t)}</a></li>' for i,t in enumerate(a['toc']))+'</ul></nav>'
    content=f'''<header class="notes-hero"><div class="notes-shell"><p class="notes-crumb"><a href="/">ホーム</a> / <a href="/notes/">実践ノート</a></p><p class="eyebrow">PRACTICE NOTES / {a['date']}</p><h1>{escape(a['title'])}</h1><p>{escape(a['description'])}</p><p class="notes-credit">制作・編集：株式会社ヒロメル</p></div></header><section class="notes-content"><div class="notes-shell">{toc}<article>{body}</article><aside class="notes-author"><b>株式会社ヒロメルの実践ノート</b><p>自社の作業・判断・検証記録をもとに制作しています。記録で確認できる内容と、まだ検証していない成果を区別して紹介します。</p><a href="/#company">会社情報</a> / <a href="mailto:contact@hiromeru-inc.com">内容に関するお問い合わせ</a></aside><div class="notes-cta"><h2>今ある仕事から、AIの使いどころを。</h2><p>公式LINEのAI応対や業務へのAI導入について、ご相談いただけます。</p><a href="https://lin.ee/5yEYApJ">LINEで相談する →</a><a href="/#services">サービス内容を見る →</a></div></div></section>'''
    page(path,a['title']+'｜株式会社ヒロメル',a['description'],content,[
        {'@type':'BlogPosting','@id':SITE+path+'#article','headline':a['title'],'description':a['description'],
         'datePublished':a['date'],'dateModified':a.get('updated',a['date']),'inLanguage':'ja','mainEntityOfPage':SITE+path,
         'author':{'@type':'Organization','name':ORG['name'],'url':SITE+'/#company'},'publisher':{'@id':ORG['@id']},'image':SITE+'/assets/og-image-v2.jpg'},
        {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'ホーム','item':SITE+'/'},
          {'@type':'ListItem','position':2,'name':'実践ノート','item':SITE+'/notes/'},{'@type':'ListItem','position':3,'name':a['title'],'item':SITE+path}]}])
    cards.append(f'<a class="notes-card" href="{path}"><time datetime="{a["date"]}">{a["date"]}</time><h2>{escape(a["title"])}</h2><p>{escape(a["description"])}</p><span>記事を読む →</span></a>')
    urls.append((path,a.get('updated',a['date'])))
page('/notes/','AI導入・業務自動化の実践ノート｜株式会社ヒロメル','自社でAIを使った業務、つまずいた箇所、処理を見直した記録を紹介します。',
     '<header class="notes-hero"><div class="notes-shell"><p class="notes-crumb"><a href="/">ホーム</a> / 実践ノート</p><p class="eyebrow">PRACTICE NOTES</p><h1>自分たちで使い、<br>見直した記録。</h1><p>AIを業務に組み込んで、何が起きたか。<br>実際の作業と判断から紹介します。</p></div></header><section class="notes-content"><div class="notes-shell">'+''.join(cards)+'</div></section>',
     [{'@type':'CollectionPage','url':SITE+'/notes/','name':'AI導入・業務自動化の実践ノート','publisher':{'@id':ORG['@id']}}])
root=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
for path,date in urls:
    entry=ET.SubElement(root,'url');ET.SubElement(entry,'loc').text=SITE+path;ET.SubElement(entry,'lastmod').text=date
ET.indent(root,space='  ')
(ROOT/'sitemap.xml').write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+SITE+'/sitemap.xml\n')
print(f'Built {len(articles)} articles, notes index, homepage schema and {len(urls)} sitemap URLs.')
