#!/usr/bin/env python3
"""Build columns, service pages and sitemap using the existing site header/footer."""
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
articles = json.loads((ROOT/'src/notes/articles.json').read_text())

def card(a, level=2):
    if a['visual']=='rule':
        visual='<span class="card-graphic graphic-rule" aria-hidden="true"><span>50<small>字 / 1件</small></span><i>×</i><span>10<small>件まで</small></span></span>'
    else:
        visual='<span class="card-graphic graphic-flow" aria-hidden="true"><span>取得</span><i>→</i><span>判断</span><i>→</i><span>通知</span></span>'
    return f'<a class="column-card" href="{a["path"]}">{visual}<div class="column-card-body"><span class="card-meta"><span>{escape(a["category"])}</span><time datetime="{a["date"]}">{a["date"].replace("-", ".")}</time></span><h{level}>{escape(a["title"])}</h{level}><p>{escape(a["description"])}</p><span class="card-read">記事を読む <span aria-hidden="true">↗</span></span></div></a>'

home_columns='<section class="section home-columns" id="notes" aria-labelledby="notes-title"><div class="shell"><div class="column-section-head"><div><p class="eyebrow">COLUMN / ヒロメルのコラム</p><h2 id="notes-title">使って、気づいて、<br>仕事を変える。</h2></div><a class="text-link" href="/column/">コラムをすべて見る <span aria-hidden="true">↗</span></a></div><div class="column-grid">'+''.join(card(a,3) for a in articles[:2])+'</div></div></section>'
home=re.sub(r'<!-- columns-home:start -->.*?<!-- columns-home:end -->','<!-- columns-home:start -->'+home_columns+'<!-- columns-home:end -->',home,flags=re.S)
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

urls=[('/',DATE),('/column/',max(a['date'] for a in articles))]
for a in articles:
    path=a['path']
    body=(ROOT/'src/notes'/f"{a['slug']}.html").read_text()
    toc='<nav class="notes-toc" aria-label="目次"><b>この記事の内容</b><ul>'+''.join(f'<li><a href="#s{i+1}">{escape(t)}</a></li>' for i,t in enumerate(a['toc']))+'</ul></nav>'
    related=''.join(f'<a href="{other["path"]}">{escape(other["title"])} <span aria-hidden="true">↗</span></a>' for other in articles if other['slug']!=a['slug'])
    content=f'''<header class="notes-hero"><div class="notes-shell"><p class="notes-crumb"><a href="/">ホーム</a> / <a href="/column/">コラム</a></p><p class="eyebrow">COLUMN / {escape(a['category'])} / {a['date']}</p><h1>{escape(a['title'])}</h1><p>{escape(a['description'])}</p><p class="notes-credit">制作・編集：株式会社ヒロメル</p></div></header><section class="notes-content"><div class="notes-shell">{toc}<article>{body}</article><aside class="notes-author"><b>株式会社ヒロメルのコラム</b><p>自社の作業・判断・検証記録をもとに制作しています。記録で確認できる内容と、まだ検証していない成果を区別して紹介します。</p><a href="/#company">会社情報</a> / <a href="mailto:contact@hiromeru-inc.com">内容に関するお問い合わせ</a></aside><aside class="related-columns"><h2>あわせて読む</h2>{related}<a href="/column/">コラム一覧へ →</a></aside><div class="notes-cta"><h2>今ある仕事から、AIの使いどころを。</h2><p>公式LINEのAI応対や業務へのAI導入について、ご相談いただけます。</p><a href="https://lin.ee/5yEYApJ">LINEで相談する →</a><a href="{a['service']}">業務へのAI導入支援を見る →</a></div></div></section>'''
    page(path,a['title']+'｜株式会社ヒロメル',a['description'],content,[
        {'@type':'BlogPosting','@id':SITE+path+'#article','headline':a['title'],'description':a['description'],
         'datePublished':a['date'],'dateModified':a.get('updated',a['date']),'inLanguage':'ja','mainEntityOfPage':SITE+path,
         'author':{'@type':'Organization','name':ORG['name'],'url':SITE+'/#company'},'publisher':{'@id':ORG['@id']},'image':SITE+'/assets/og-image-v2.jpg'},
        {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'ホーム','item':SITE+'/'},
          {'@type':'ListItem','position':2,'name':'コラム','item':SITE+'/column/'},{'@type':'ListItem','position':3,'name':a['title'],'item':SITE+path}]}])
    urls.append((path,a.get('updated',a['date'])))
page('/column/','コラム｜AI導入・業務自動化の実践記録｜株式会社ヒロメル','ヒロメルが自社でAIを使い、業務を見直した記録。通知の設計やタスクリストの改善など、実際の作業から紹介します。',
     '<header class="column-hero"><div class="shell"><p class="notes-crumb"><a href="/">ホーム</a> / コラム</p><div class="column-hero-grid"><div><p class="eyebrow">HIROMERU COLUMN</p><h1>使って、気づいて、<br><em>仕事を変える。</em></h1><p>AIを仕事に組み込んで、何が起きたか。<br>つまずきも、工夫も。自分たちの現場から。</p></div><div class="column-symbol" aria-hidden="true"><span>TRY.<br>LEARN.<br>UPDATE.</span><i>↗</i></div></div><nav class="column-topics" aria-label="コラムの案内"><a href="#articles">自社の運用記録 ↓</a><a href="/services/line-ai/">公式LINEのAI連携 ↗</a><a href="/services/ai-workflow/">業務へのAI導入 ↗</a></nav></div></header><section class="column-list" id="articles" aria-labelledby="articles-title"><div class="shell"><div class="column-list-heading"><h2 id="articles-title">実践から、ひとつずつ。</h2><p>'+str(len(articles))+' ARTICLES</p></div><div class="column-grid">'+''.join(card(a) for a in articles)+'</div><div class="column-editorial"><h2>ここに残すのは、自分たちで確かめたこと。</h2><p>実際に変えた手順や、作ったものをもとに書いています。社内での検証とお客様への導入事例、変更した設定と確認できた成果を分けてお伝えします。</p></div></div></section>',
     [{'@type':'CollectionPage','@id':SITE+'/column/#collection','url':SITE+'/column/','name':'ヒロメルのコラム','publisher':{'@id':ORG['@id']},'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':a['title'],'url':SITE+a['path']} for i,a in enumerate(articles)]}}])

# Preserve the published article URL; move only the old index to the column hub.
(ROOT/'notes/index.html').write_text('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0;url=/column/"><link rel="canonical" href="'+SITE+'/column/"><title>コラムへ移動｜株式会社ヒロメル</title></head><body><h1>ヒロメルのコラム</h1><p><a href="/column/">コラム一覧へ移動する</a></p></body></html>\n')

services=[
 {'slug':'line-ai','name':'公式LINEのAI連携・導入支援','eyebrow':'LINE × AI','headline':'届いた声に答える。<br><em>次の会話につなげる。</em>','description':'よくある質問への回答、予約の希望受付、担当者への引き継ぎ。公式LINEのAI応対を、御社の情報と業務に合わせて設計します。','image':'service-line-photo-v2-768.webp','alt':'店舗でスマートフォンの問い合わせを確認するイメージ'},
 {'slug':'ai-workflow','name':'業務へのAI導入・自動化支援','eyebrow':'AI FOR YOUR WORK','headline':'日々の仕事に、<br><em>使い続けられるAIを。</em>','description':'返信の下書き、日報、情報の整理・集計。いまの業務を棚卸しし、小さな試作から導入・運用の調整まで支援します。','image':'service-ai-photo-v2-768.webp','alt':'資料を広げて業務の進め方を整理するイメージ'}]
for s in services:
    path='/services/'+s['slug']+'/'
    content=f'<header class="service-detail-hero"><div class="shell"><p class="notes-crumb"><a href="/">ホーム</a> / {s["name"]}</p><div class="service-detail-lead"><div><p class="eyebrow">{s["eyebrow"]}</p><p class="service-detail-name">{s["name"]}</p><h1>{s["headline"]}</h1><p>{s["description"]}</p><a class="detail-primary" href="https://lin.ee/5yEYApJ">この業務について相談する <span aria-hidden="true">↗</span></a></div><figure><img src="/assets/{s["image"]}" alt="{s["alt"]}" width="768" height="512"><figcaption>業務のイメージ</figcaption></figure></div></div></header>'
    content+=(ROOT/'src/services'/f'{s["slug"]}.html').read_text()
    content+='<section class="detail-contact"><div class="shell"><p class="eyebrow">LET’S TALK</p><h2>いまの仕事を、聞かせてください。</h2><p>やりたいことが、まだまとまっていなくても大丈夫。<br>今ある情報から、最初の実例を一緒に考えます。</p><a class="detail-primary" href="https://lin.ee/5yEYApJ">LINEで相談する ↗</a><a class="detail-email" href="mailto:contact@hiromeru-inc.com">メールで相談する ↗</a><a class="detail-email" href="/column/">ヒロメルのコラムを読む ↗</a></div></section>'
    page(path,s['name']+'｜株式会社ヒロメル',s['description'],content,[{'@type':'Service','@id':SITE+path+'#service','name':s['name'],'url':SITE+path,'description':s['description'],'provider':{'@id':ORG['@id']}},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'ホーム','item':SITE+'/'},{'@type':'ListItem','position':2,'name':s['name'],'item':SITE+path}]}])
    urls.append((path,DATE))
root=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
for path,date in urls:
    entry=ET.SubElement(root,'url');ET.SubElement(entry,'loc').text=SITE+path;ET.SubElement(entry,'lastmod').text=date
ET.indent(root,space='  ')
(ROOT/'sitemap.xml').write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+SITE+'/sitemap.xml\n')
print(f'Built {len(articles)} articles, column index, {len(services)} services and {len(urls)} canonical sitemap URLs.')
