---
layout: page
title: 文章
permalink: /essays/
lang: zh
description: 玉书房关于重大、长期、难以逆转的家庭决策的原创文章。
---

{% if site.posts.size > 0 %}
<ul class="post-list">
{% for post in site.posts %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y-%m-%d" }}</time>
    {% if post.description %}<p class="excerpt">{{ post.description }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
{% else %}

第一批文章正在写。

玉书房只写那些重要、长期、代价高、难以逆转的决定——教育、地域、婚姻、事业、财富、传承。不写流程，不写清单，不写攻略。

新文章发布时，订阅者会收到。

{% endif %}
