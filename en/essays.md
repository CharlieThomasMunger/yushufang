---
layout: page
title: Essays
permalink: /en/essays/
lang: en
noindex: true
description: Selected essays from The Jade Study, in English.
---

<!-- ⚠️ 英文版待 James 确认后发布。确认后删掉 front matter 里的 noindex 一行。 -->

{% if site.en.size > 0 %}
<ul class="post-list">
{% for item in site.en %}
  <li>
    <a href="{{ item.url | relative_url }}">{{ item.title }}</a>
    {% if item.date %}<time datetime="{{ item.date | date_to_xmlschema }}">{{ item.date | date: "%Y-%m-%d" }}</time>{% endif %}
    {% if item.description %}<p class="excerpt">{{ item.description }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
{% else %}

Selected essays will appear here in English. The main body of work is published in Chinese — see [中文站](/essays/).

{% endif %}
