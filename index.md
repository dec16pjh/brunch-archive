---
layout: default
title: 홈
---

<div class="home-intro">
  <p>박종호 작가의 브런치 서랍(미발행 초고)과 브런치북을 장르별로 정리한 아카이브입니다.</p>
</div>

{% assign books = site.brunchbooks | where: "layout", "book_index" %}
{% assign mags = site.magazines | where: "layout", "book_index" %}
{% assign all_items = books | concat: mags %}
{% assign genres = all_items | group_by: "genre" %}

{% for g in genres %}
<section class="genre-section">
  <h2 class="genre-title">{{ g.name | escape }}</h2>
  <ul class="book-list">
    {% for b in g.items %}
    <li>
      <a href="{{ b.url | relative_url }}">{{ b.title | escape }}</a>
      <span class="book-list-meta">{{ b.author | escape }} · {{ b.release_date }}</span>
    </li>
    {% endfor %}
  </ul>
</section>
{% endfor %}
