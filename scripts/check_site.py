"""Validate the rendered public site with the Python standard library."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, sys
from datetime import datetime
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
    author='刘一卜' if page.lang=='zh-Hans' else 'Liu Yibu'
    if page.meta.get('author')!=author:failures.append(name+': incorrect author')
    title_match=re.search(r'<title>(.*?)</title>', text)
    title_text=title_match.group(1) if title_match else ''
    if 'fonts.googleapis.com' in text or 'fonts.gstatic.com' in text:
        failures.append(name+': external font request')
    brand_pages={
        'index.html','about/index.html','essays/index.html','concepts/index.html','books/gaiming/index.html',
        'editorial/index.html','family-decisions/index.html','contact/index.html','en/index.html','en/about/index.html',
        'en/essays/index.html','fr/index.html','fr/about/index.html','fr/essays/index.html'
    }
    if name in brand_pages and ('玉书房' not in title_text or '刘一卜' not in title_text):
        failures.append(name+': title does not pair 玉书房 with 刘一卜')
    if page.lang=='zh-Hans' and name in brand_pages:
        cjk=len(re.findall(r'[\u4e00-\u9fff]', title_text))
        desc_cjk=len(re.findall(r'[\u4e00-\u9fff]', page.meta.get('description','')))
        if cjk>30:failures.append(name+': title is longer than 30 Chinese characters')
        if desc_cjk>80:failures.append(name+': description is longer than 80 Chinese characters')
        if '玉书房' not in page.meta.get('description','') or '刘一卜' not in page.meta.get('description',''):
            failures.append(name+': description does not pair 玉书房 with 刘一卜')
    if re.search(r'James|KIT_FORM_ID|YC001|YB001|YN___|设计预览|公共表达候选|localhost|127\.0\.0\.1|\{%|\{\{',text,re.I):failures.append(name+': preview, internal or unresolved content')
    if not page.jsons:failures.append(name+': missing structured data')
    entities=[]
    for block in page.jsons:
        entities.extend(block.get('@graph', [block]))
    page_entities=[item for item in entities if item.get('@type') in ['WebPage','AboutPage','ContactPage','Article']]
    if len(page_entities)!=1:failures.append(name+': expected one page entity')
    by_id={item.get('@id'):item for item in entities if item.get('@id')}
    website=by_id.get(base+'/#website',{})
    organization=by_id.get(base+'/#organization',{})
    person=by_id.get(base+'/#author',{})
    if website.get('@type')!='WebSite' or website.get('url')!=base+'/':failures.append(name+': missing website identity')
    if '玉书房' not in website.get('name','') or '刘一卜' not in website.get('name',''):failures.append(name+': website name does not pair 玉书房 with 刘一卜')
    if organization.get('name')!='玉书房' or organization.get('email')!='liuyibu01@gmail.com':failures.append(name+': publisher identity mismatch')
    org_names=organization.get('alternateName') or []
    if isinstance(org_names,str):org_names=[org_names]
    if '玉书房' not in ' '.join(org_names) or '刘一卜' not in ' '.join(org_names):failures.append(name+': organization name does not pair 玉书房 with 刘一卜')
    if person.get('name')!=author or set(person.get('alternateName',[]))!={'刘一卜','Liu Yibu'}:failures.append(name+': person identity mismatch')
    if '刘一卜' not in person.get('description','') or '玉书房' not in person.get('description',''):failures.append(name+': person description does not pair 玉书房 with 刘一卜')
    for label,entity in (('website',website),('organization',organization),('person',person)):
        same=entity.get('sameAs')
        if not isinstance(same,list) or not same:failures.append(name+': missing sameAs on '+label);continue
        for same_url in same:
            if not isinstance(same_url,str) or not same_url.startswith(base+'/'):failures.append(name+': sameAs leaves the site '+str(same_url));continue
            same_target=resolve(urlsplit(same_url).path,name)
            if same_target not in pages:failures.append(name+': sameAs target missing '+same_url)
    for item in page_entities:
        if not item.get('name') or item.get('url')!=expected:failures.append(name+': page entity identity mismatch')
        if item.get('isPartOf',{}).get('@id')!=base+'/#website':failures.append(name+': website relationship missing')
        if item.get('publisher',{}).get('@id')!=base+'/#organization':failures.append(name+': publisher relationship missing')
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
        sitemap_root=ET.parse(sitemap).getroot()
        locations=[x.text for x in sitemap_root.iter() if x.tag.endswith('}loc')]
        dates={entry.find('{*}loc').text:entry.findtext('{*}lastmod') for entry in sitemap_root}
        for location in locations:
            target=resolve(urlsplit(location).path,'index.html')
            if target not in pages:failures.append('Sitemap contains non-page '+str(location))
            elif 'noindex' in pages[target].meta.get('robots',''):failures.append('Sitemap contains noindex page '+target)
            else:
                for block in pages[target].jsons:
                    for item in block.get('@graph',[block]):
                        if item.get('@type')=='Article':
                            try:
                                modified=datetime.fromisoformat(item['dateModified'].replace('Z','+00:00'))
                                listed=datetime.fromisoformat((dates.get(location) or '').replace('Z','+00:00'))
                                if modified!=listed:failures.append(target+': sitemap and article update dates disagree')
                            except (ValueError,KeyError):failures.append(target+': missing or invalid article sitemap date')
                if not dates.get(location):failures.append('Sitemap missing lastmod '+target)
                else:
                    try:datetime.fromisoformat(dates[location].replace('Z','+00:00'))
                    except ValueError:failures.append('Sitemap invalid lastmod '+target)
        for name,p in pages.items():
            if 'noindex' not in p.meta.get('robots','') and base+route(name) not in locations:failures.append('Indexable page absent from sitemap '+name)
    except ET.ParseError:failures.append('Malformed sitemap XML')

feed_path=root/'feed.xml'
essay_urls=[
    base+'/essays/where-yushufang-comes-from/',
    base+'/essays/options-before-choice/',
    base+'/essays/decision-floor-and-upside/',
    base+'/essays/when-good-advice-conflicts/',
    base+'/essays/opportunity-and-options/',
    base+'/essays/the-structure-of-fate/',
    base+'/essays/effort-choice-and-layout/',
    base+'/essays/fate-change-and-chance/',
]
if not feed_path.is_file():failures.append('Missing feed')
else:
    try:
        feed_root=ET.parse(feed_path).getroot()
        found=set()
        for entry in feed_root:
            if not entry.tag.endswith('entry'):continue
            for child in entry:
                if child.tag.endswith('link') and child.get('rel')=='alternate' and child.get('href'):
                    found.add(child.get('href').rstrip('/'))
        if len(found)<len(essay_urls):failures.append('Feed has '+str(len(found))+' entries')
        for essay_url in essay_urls:
            if essay_url.rstrip('/') not in found:failures.append('Feed missing '+essay_url)
    except ET.ParseError:failures.append('Malformed feed XML')

llms_path=root/'llms.txt'
if not llms_path.is_file():failures.append('Missing llms.txt')
else:
    llms=llms_path.read_text(encoding='utf-8')
    if '玉书房' not in llms or '刘一卜' not in llms:failures.append('llms.txt does not identify 玉书房 · 刘一卜')
    for essay_url in essay_urls:
        if essay_url not in llms:failures.append('llms.txt missing '+essay_url)

robots=(root/'robots.txt').read_text(encoding='utf-8') if (root/'robots.txt').is_file() else ''
if 'Disallow: /' in robots:failures.append('robots.txt disallows the site')
if 'Allow: /' not in robots:failures.append('robots.txt missing allow rule')
for bot in ['Baiduspider','360Spider','Sogou web spider','Bytespider','GPTBot']:
    if bot not in robots:failures.append('robots.txt missing '+bot)

css=(root/'assets/site.css').read_text(encoding='utf-8') if (root/'assets/site.css').is_file() else ''
for token in ['Songti SC','SimSun','STSong']:
    if token not in css:failures.append('Chinese serif stack missing '+token)
if css.find("'SimSun'") > css.find("'STSong'"):failures.append('STSong precedes SimSun in the serif stack')
if 'fonts.googleapis.com' in css or 'fonts.gstatic.com' in css or '@font-face' in css:
    failures.append('CSS loads an external or embedded font')

for asset in ['favicon.ico','apple-touch-icon.png','assets/icons/favicon-32.png','assets/icons/icon-192.png']:
    if not (root/asset).is_file():failures.append('Missing '+asset)

for internal in ['INSTALL.md','scripts/check_site.py','_drafts/TEMPLATE.md','public-history.json','page-manifest.json','compare.html','07.html']:
    if (root/internal).exists():failures.append('Internal/review asset copied to site: '+internal)

print(json.dumps({'html_pages':len(pages),'checked_links':checked,'errors':failures},ensure_ascii=False))
sys.exit(1 if failures else 0)
