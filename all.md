---
layout: default
title: All tips
permalink: /all/
---

# All tips

{% assign tips = site.tips | sort: "date" | reverse %}
{% if tips.size == 0 %}
<p class="notice">Nothing published yet.</p>
{% else %}

{% for surface in site.data.surfaces %}
{% assign group = tips | where: "surface", surface.slug %}
{% if group.size > 0 %}
<h2>{{ surface.label }}</h2>
<ul class="tip-list">
  {% for tip in group %}
  <li>
    <a href="{{ tip.url | relative_url }}">{{ tip.title | escape }}</a>
    <span class="meta">Tip #{{ tip.tip_number }} &middot; {{ tip.date | date: "%d %b %Y" }}</span>
  </li>
  {% endfor %}
</ul>
{% endif %}
{% endfor %}

{% endif %}
