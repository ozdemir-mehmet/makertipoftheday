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
<div class="group">
  <h2>{{ surface.label | escape }}</h2>
  <p class="count">{{ group.size }} tip{% if group.size != 1 %}s{% endif %}</p>
  <ul class="feed">
    {% for tip in group %}
    <li>
      <span class="when">{% if tip.tip_number %}#{{ tip.tip_number }} &middot; {% endif %}{{ tip.date | date: "%-d %b %Y" }}</span>
      <span class="what"><a href="{{ tip.url | relative_url }}">{{ tip.title | escape }}</a></span>
    </li>
    {% endfor %}
  </ul>
</div>
{% endif %}
{% endfor %}

{% endif %}
