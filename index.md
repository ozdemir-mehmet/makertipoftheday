---
layout: default
title: Latest tips
---

# {{ site.title }}

{{ site.description }}

{% assign tips = site.tips | sort: "date" | reverse %}
{% if tips.size == 0 %}
<p class="notice">No tips published yet. The scaffold is live and the first tip lands once it has
been executed and evidenced.</p>
{% else %}
<ul class="tip-list">
  {% for tip in tips limit: 10 %}
  <li>
    <a href="{{ tip.url | relative_url }}">{{ tip.title | escape }}</a>
    <span class="meta">
      <span class="surface">{% include surface-label.html surface=tip.surface %}</span>
      {{ tip.date | date: "%d %b %Y" }} &middot; {% include tip-status.html tip=tip mode="line" %}
    </span>
  </li>
  {% endfor %}
</ul>
<p><a href="{{ '/all/' | relative_url }}">All {{ tips.size }} tips</a></p>
{% endif %}
