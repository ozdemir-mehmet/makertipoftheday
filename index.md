---
layout: default
title: Latest tips
---

{% assign tips = site.tips | sort: "date" | reverse %}
{% if tips.size == 0 %}
<h1>{{ site.title | escape }}</h1>
<p class="notice">No tips published yet. The scaffold is live and the first tip lands once it has
been executed and evidenced.</p>
{% else %}
{% assign lead = tips.first %}

<p class="kicker">
  <span class="surface" data-s="{{ lead.surface | escape }}">{% include surface-label.html surface=lead.surface %}</span>
  {% if lead.tip_number %}<span>Tip #{{ lead.tip_number | escape }}</span>{% endif %}
  {% if lead.date %}<time datetime="{{ lead.date | date_to_xmlschema }}">{{ lead.date | date: "%-d %b %Y" }}</time>{% endif %}
</p>

<h1>{{ lead.title | escape }}</h1>

{% if lead.summary %}<p class="summary">{{ lead.summary | escape }}</p>{% endif %}

<p><a class="readmore" href="{{ lead.url | relative_url }}">Read the tip &rarr;</a></p>

<div class="section-head">
  <h2>Every tip</h2>
  <span>{{ tips.size }} published</span>
</div>

<ul class="feed">
  {% for tip in tips %}
  <li>
    <span class="when">{{ tip.date | date: "%-d %b %Y" }}</span>
    <span class="what"><a href="{{ tip.url | relative_url }}">{{ tip.title | escape }}</a></span>
    <span class="surface" data-s="{{ tip.surface | escape }}">{% include surface-label.html surface=tip.surface %}</span>
  </li>
  {% endfor %}
</ul>
{% endif %}
