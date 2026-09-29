"""Validate the rendered public site with the Python standard library."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, sys
import xml.etree.ElementTree as ET

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site').resolve()
base='https://yushufang.org'
failures=[]

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=set();self.headings=0;self.canon=[];self.lang='';self.alternates={};self.meta={};self.jsons=[];self.capture=False;self.buffer='';self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='html':self.lang=a.get('lang','')
        if tag=='h1':self.headings+=1
        if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical':self.canon.append(a.get('href'))
        if tag=='link' and a.get('hreflang'):self.alternates[a['hreflang']]=a.get('href')
        if tag=='script' and a.get('type')=='application/ld+json':self.capture=True;self.buffer=''
        for key in ['href','src']:
            if key in a:self.links.append(a[key])
    def handle_data(self,data):
        if self.capture:self.buffer+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.capture:
            try:self.jsons.append(json.loads(self.buffer))
            except ValueError:failures.append('Invalid structured data')
            self.capture=False

pages={p.relative_to(root).as_posix():Page(p.read_text(encoding='utf-8')) for p in root.rglob('*.html')}
required=['index.html','about/index.html','essays/index.html','en/index.html','en/about/index.html','en/essays/index.html','fr/index.html','fr/about/index.html','fr/essays/index.html','concepts/index.html','books/gaiming/index.html','editorial/index.html']
for path in required:
    if path not in pages:failures.append('Missing page: '+path)

def route(filename):
    return '/'+filename[:-10] if filename.endswith('index.html') else '/'+filename

def resolve(path,current):
    if not path:return current
    local=path.lstrip('/') if path.startswith('/') else str(Path(current).parent/path).replace('\\','/')
    if local.endswith('/') or not local:local+='index.html'
    return local

checked=0
for name,page in pages.items():
    text=(root/name).read_text(encoding='utf-8')
    expected=base+route(name)
    if page.canon!=[expected]:failures.append(name+': incorrect canonical '+str(page.canon))
    if page.headings!=1:failures.append(name+': expected one h1')
    if not page.meta.get('description'):failures.append(name+': no description')
    author='修印先生' if page.lang=='zh-Hans' else 'Mr Xiuyin'
    if page.meta.get('author')!=author:failures.append(name+': incorrect author')
    if re.search(r'James|KIT_FORM_ID|YC001|YB001|YN___|设计预览|公共表达候选|localhost|127\.0\.0\.1|\{%|\{\{',text,re.I):failures.append(name+': preview, internal or unresolved content')
    if not page.jsons:failures.append(name+': missing structured data')
    for item in page.jsons:
        if item.get('author',{}).get('name')!=author:failures.append(name+': schema author mismatch')
        if item.get('inLanguage')!=page.lang:failures.append(name+': schema language mismatch')
        if item.get('@type')=='Article' and not all(item.get(k) for k in ['datePublished','dateModified','version']):failures.append(name+': article dates/version missing')
    for lang,alt in page.alternates.items():
        if lang=='x-default':continue
        target=resolve(urlsplit(alt).path,name)
        if target not in pages or pages[target].alternates.get(page.lang)!=expected:failures.append(name+': hreflang is not reciprocal')
    for link in page.links:
        u=urlsplit(link)
        if u.scheme in ['mailto','tel']:continue
        if u.netloc and u.netloc!='yushufang.org':continue
        target=resolve(unquote(u.path),name)
        checked+=1
        if not (root/target).is_file():failures.append(name+': missing target '+link)
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:failures.append(name+': missing anchor '+link)

sitemap=root/'sitemap.xml'
if not sitemap.is_file():failures.append('Missing sitemap')
else:
    try:
        locations=[x.text for x in ET.parse(sitemap).iter() if x.tag.endswith('}loc')]
        for location in locations:
            target=resolve(urlsplit(location).path,'index.html')
            if target not in pages:failures.append('Sitemap contains non-page '+str(location))
            elif 'noindex' in pages[target].meta.get('robots',''):failures.append('Sitemap contains noindex page '+target)
        for name,p in pages.items():
            if 'noindex' not in p.meta.get('robots','') and base+route(name) not in locations:failures.append('Indexable page absent from sitemap '+name)
    except ET.ParseError:failures.append('Malformed sitemap XML')

for internal in ['INSTALL.md','scripts/check_site.py','_drafts/TEMPLATE.md','public-history.json','page-manifest.json','compare.html','07.html']:
    if (root/internal).exists():failures.append('Internal/review asset copied to site: '+internal)

print(json.dumps({'html_pages':len(pages),'checked_links':checked,'errors':failures},ensure_ascii=False))
sys.exit(1 if failures else 0)
